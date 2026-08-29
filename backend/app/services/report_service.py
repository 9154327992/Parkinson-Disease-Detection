from datetime import datetime
from pathlib import Path
from typing import List, Optional
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)

from app.database.database import SessionLocal

from app.database.models import (
    Patient,
    Prediction,
    Report,
)

from app.schemas.report import (
    ReportRequest,
    ReportResponse,
    ReportMetadata,
    ReportPatient,
    PredictionSummary,
    RecommendationItem,
    ExerciseItem,
    MedicationItem,
    FollowUpPlan,
    ReportSummary,
    ReportList,
    DeleteReportResponse,
)

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)


# ==========================================================
# Paths
# ==========================================================

# report_service.py
#   app/
#     services/
#
# Project root:
#   backend/
#
# PDF directory:
#   backend/reports/

SERVICE_FILE = Path(__file__).resolve()

BACKEND_DIR = SERVICE_FILE.parents[2]

REPORTS_DIR = BACKEND_DIR / "reports"

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# Report Service
# ==========================================================

class ReportService:
    """
    Handles patient report generation.

    Reports are stored in the database and the generated
    PDF files are stored in backend/reports/.
    """

    # ======================================================
    # Generate Report From Prediction
    # ======================================================

    def generate_from_prediction(
        self,
        request: PredictionRequest,
        prediction: PredictionResponse,
    ) -> ReportResponse:
        """
        Generate a report from a completed prediction.

        Steps:
            1. Validate prediction.
            2. Find patient.
            3. Create database report.
            4. Generate PDF.
            5. Save PDF to backend/reports/.
            6. Store PDF path in report_path.
            7. Return report response.
        """

        db = SessionLocal()

        try:

            # --------------------------------------------------
            # Find Prediction
            # --------------------------------------------------

            prediction_record = (
                db.query(Prediction)
                .filter(
                    Prediction.id == prediction.prediction_id
                )
                .first()
            )

            if prediction_record is None:

                raise ValueError(
                    "Prediction not found."
                )

            # --------------------------------------------------
            # Verify Patient
            # --------------------------------------------------

            if (
                prediction_record.patient_id
                != prediction.patient_id
            ):

                raise ValueError(
                    "Prediction does not belong "
                    "to the requested patient."
                )

            patient = prediction_record.patient

            if patient is None:

                raise ValueError(
                    "Patient not found."
                )

            # --------------------------------------------------
            # Create Database Report
            # --------------------------------------------------

            database_report = Report(
                patient_id=patient.id,

                prediction_id=prediction_record.id,

                report_name=(
                    "Parkinson Disease "
                    "Assessment Report"
                ),

                report_path=None,

                generated_at=datetime.utcnow(),
            )

            db.add(database_report)

            db.commit()

            db.refresh(database_report)

            # --------------------------------------------------
            # Build Report Response
            # --------------------------------------------------

            report_response = (
                self._build_report_response(
                    report_id=database_report.id,
                    patient=patient,
                    prediction=prediction,
                )
            )

            # --------------------------------------------------
            # Generate PDF
            # --------------------------------------------------

            pdf_bytes, filename = (
                self._generate_pdf(
                    report_response
                )
            )

            # --------------------------------------------------
            # Save PDF
            # --------------------------------------------------

            pdf_path = (
                REPORTS_DIR / filename
            )

            pdf_path.write_bytes(
                pdf_bytes
            )

            # --------------------------------------------------
            # Store PDF Path
            # --------------------------------------------------

            database_report.report_path = (
                str(pdf_path)
            )

            db.commit()

            db.refresh(
                database_report
            )

            return report_response

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    # ==========================================================
    # Generate Manual Report
    # ==========================================================

    def generate_report(
        self,
        request: ReportRequest,
    ) -> ReportResponse:
        """
        Generate a report manually for an existing patient
        and prediction.
        """

        db = SessionLocal()

        try:

            # --------------------------------------------------
            # Find Patient
            # --------------------------------------------------

            patient = (
                db.query(Patient)
                .filter(
                    Patient.id
                    == request.patient_id
                )
                .first()
            )

            if patient is None:

                raise ValueError(
                    "Patient not found."
                )

            # --------------------------------------------------
            # Find Exact Prediction
            # --------------------------------------------------

            prediction_record = (
                db.query(Prediction)
                .filter(
                    Prediction.id
                    == request.prediction_id,

                    Prediction.patient_id
                    == patient.id,
                )
                .first()
            )

            if prediction_record is None:

                raise ValueError(
                    "Prediction not found "
                    "for this patient."
                )

            # --------------------------------------------------
            # Build Prediction Response
            # --------------------------------------------------

            prediction = (
                self._prediction_response(
                    prediction_record,
                    patient.id,
                )
            )

            # --------------------------------------------------
            # Create Database Report
            # --------------------------------------------------

            database_report = Report(
                patient_id=patient.id,

                prediction_id=prediction_record.id,

                report_name=(
                    "Parkinson Disease "
                    "Assessment Report"
                ),

                report_path=None,

                generated_at=datetime.utcnow(),
            )

            db.add(
                database_report
            )

            db.commit()

            db.refresh(
                database_report
            )

            # --------------------------------------------------
            # Build Report Response
            # --------------------------------------------------

            report_response = (
                self._build_report_response(
                    report_id=database_report.id,

                    patient=patient,

                    prediction=prediction,

                    include_recommendations=(
                        request.include_recommendations
                    ),

                    include_exercises=(
                        request.include_exercises
                    ),

                    include_medication=(
                        request.include_medication
                    ),

                    include_follow_up=(
                        request.include_follow_up
                    ),

                    doctor_notes=(
                        request.doctor_notes
                    ),
                )
            )

            # --------------------------------------------------
            # Generate PDF
            # --------------------------------------------------

            pdf_bytes, filename = (
                self._generate_pdf(
                    report_response
                )
            )

            # --------------------------------------------------
            # Save PDF
            # --------------------------------------------------

            pdf_path = (
                REPORTS_DIR / filename
            )

            pdf_path.write_bytes(
                pdf_bytes
            )

            # --------------------------------------------------
            # Save Path In Database
            # --------------------------------------------------

            database_report.report_path = (
                str(pdf_path)
            )

            db.commit()

            db.refresh(
                database_report
            )

            return report_response

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    # ==========================================================
    # Build Report Response
    # ==========================================================

    def _build_report_response(
        self,
        report_id: int,
        patient: Patient,
        prediction: PredictionResponse,
        include_recommendations: bool = True,
        include_exercises: bool = True,
        include_medication: bool = True,
        include_follow_up: bool = True,
        doctor_notes: Optional[str] = None,
    ) -> ReportResponse:
        """
        Build the API report response.
        """

        # --------------------------------------------------
        # Follow-up
        # --------------------------------------------------

        if include_follow_up:

            follow_up = FollowUpPlan(
                next_visit=(
                    "As recommended by a "
                    "healthcare professional"
                ),

                specialist="Neurologist",

                notes=(
                    "Review the prediction results "
                    "with a qualified healthcare "
                    "professional."
                ),
            )

        else:

            follow_up = FollowUpPlan(
                next_visit="Not included",

                specialist="Not specified",

                notes=(
                    "Follow-up section was "
                    "not requested."
                ),
            )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        return ReportResponse(

            metadata=ReportMetadata(

                report_id=report_id,

                report_name=(
                    "Parkinson Disease "
                    "Assessment Report"
                ),

                report_type="PDF",

                generated_by="System",

                generated_at=datetime.utcnow(),

                version="1.0.0",
            ),

            patient=ReportPatient(

                patient_id=patient.id,

                full_name=(
                    f"{patient.first_name} "
                    f"{patient.last_name}"
                ).strip(),

                age=patient.age,

                gender=patient.gender,

                medical_history=None,
            ),

            prediction=PredictionSummary(

                prediction=prediction.prediction,

                confidence=prediction.confidence,

                risk_score=prediction.risk_score,

                risk_level=prediction.risk_level,

                recommendation=(
                    prediction.recommendation
                ),
            ),

            recommendations=(
                self._recommendations()
                if include_recommendations
                else []
            ),

            exercises=(
                self._exercises()
                if include_exercises
                else []
            ),

            medication=(
                self._medication()
                if include_medication
                else []
            ),

            follow_up=follow_up,

            doctor_notes=doctor_notes,
        )

    # ==========================================================
    # Generate PDF
    # ==========================================================

    def _generate_pdf(
        self,
        report: ReportResponse,
    ):
        """
        Generate a PDF from a ReportResponse.

        Returns:
            (pdf_bytes, filename)
        """

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,

            pagesize=A4,

            title=(
                "Parkinson Disease "
                "Assessment Report"
            ),
        )

        styles = (
            getSampleStyleSheet()
        )

        story = []

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        story.append(
            Paragraph(
                "Parkinson Disease Assessment Report",
                styles["Title"],
            )
        )

        story.append(
            Spacer(
                1,
                20,
            )
        )

        # --------------------------------------------------
        # Report Information
        # --------------------------------------------------

        metadata = report.metadata

        story.append(
            Paragraph(
                "<b>Report Information</b>",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Report ID:</b> "
                f"{metadata.report_id}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Generated:</b> "
                f"{metadata.generated_at}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Version:</b> "
                f"{escape(str(metadata.version))}",
                styles["Normal"],
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        # --------------------------------------------------
        # Patient Information
        # --------------------------------------------------

        patient = report.patient

        story.append(
            Paragraph(
                "Patient Information",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Patient:</b> "
                f"{escape(str(patient.full_name))}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Patient ID:</b> "
                f"{patient.patient_id}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Age:</b> "
                f"{patient.age}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Gender:</b> "
                f"{escape(str(patient.gender))}",
                styles["Normal"],
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        # --------------------------------------------------
        # Prediction Information
        # --------------------------------------------------

        prediction = report.prediction

        story.append(
            Paragraph(
                "Prediction Result",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Prediction:</b> "
                f"{escape(str(prediction.prediction))}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Confidence:</b> "
                f"{prediction.confidence}%",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Risk Score:</b> "
                f"{prediction.risk_score}%",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"<b>Risk Level:</b> "
                f"{escape(str(prediction.risk_level))}",
                styles["Normal"],
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        # --------------------------------------------------
        # Recommendation
        # --------------------------------------------------

        story.append(
            Paragraph(
                "Recommendation",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                escape(
                    str(
                        prediction.recommendation
                    )
                ),
                styles["Normal"],
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        # --------------------------------------------------
        # Recommendations
        # --------------------------------------------------

        if report.recommendations:

            story.append(
                Paragraph(
                    "Recommendations",
                    styles["Heading2"],
                )
            )

            for item in (
                report.recommendations
            ):

                story.append(
                    Paragraph(
                        (
                            f"<b>{escape(str(item.title))}"
                            f":</b> "
                            f"{escape(str(item.description))}"
                        ),
                        styles["Normal"],
                    )
                )

                story.append(
                    Spacer(
                        1,
                        5,
                    )
                )

            story.append(
                Spacer(
                    1,
                    10,
                )
            )

        # --------------------------------------------------
        # Exercises
        # --------------------------------------------------

        if report.exercises:

            story.append(
                Paragraph(
                    "Exercise Guidance",
                    styles["Heading2"],
                )
            )

            for item in report.exercises:

                story.append(
                    Paragraph(
                        (
                            f"<b>{escape(str(item.name))}"
                            f":</b> "
                            f"{escape(str(item.duration))}, "
                            f"{escape(str(item.frequency))}. "
                            f"{escape(str(item.description))}"
                        ),
                        styles["Normal"],
                    )
                )

                story.append(
                    Spacer(
                        1,
                        5,
                    )
                )

            story.append(
                Spacer(
                    1,
                    10,
                )
            )

        # --------------------------------------------------
        # Medication
        # --------------------------------------------------

        if report.medication:

            story.append(
                Paragraph(
                    "Medication Guidance",
                    styles["Heading2"],
                )
            )

            for item in report.medication:

                story.append(
                    Paragraph(
                        (
                            f"<b>{escape(str(item.title))}"
                            f":</b> "
                            f"{escape(str(item.description))}"
                        ),
                        styles["Normal"],
                    )
                )

                story.append(
                    Spacer(
                        1,
                        5,
                    )
                )

            story.append(
                Spacer(
                    1,
                    10,
                )
            )

        # --------------------------------------------------
        # Follow-up
        # --------------------------------------------------

        if report.follow_up:

            story.append(
                Paragraph(
                    "Follow-up Plan",
                    styles["Heading2"],
                )
            )

            story.append(
                Paragraph(
                    (
                        f"<b>Next Visit:</b> "
                        f"{escape(str(report.follow_up.next_visit))}"
                    ),
                    styles["Normal"],
                )
            )

            story.append(
                Paragraph(
                    (
                        f"<b>Specialist:</b> "
                        f"{escape(str(report.follow_up.specialist))}"
                    ),
                    styles["Normal"],
                )
            )

            story.append(
                Paragraph(
                    (
                        f"<b>Notes:</b> "
                        f"{escape(str(report.follow_up.notes))}"
                    ),
                    styles["Normal"],
                )
            )

            story.append(
                Spacer(
                    1,
                    15,
                )
            )

        # --------------------------------------------------
        # Doctor Notes
        # --------------------------------------------------

        if report.doctor_notes:

            story.append(
                Paragraph(
                    "Doctor Notes",
                    styles["Heading2"],
                )
            )

            story.append(
                Paragraph(
                    escape(
                        str(
                            report.doctor_notes
                        )
                    ),
                    styles["Normal"],
                )
            )

            story.append(
                Spacer(
                    1,
                    15,
                )
            )

        # --------------------------------------------------
        # Medical Disclaimer
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>Medical Disclaimer:</b> "
                "This report provides AI-assisted "
                "screening information. It does not "
                "diagnose Parkinson's disease and "
                "should not replace evaluation by "
                "a qualified healthcare professional.",
                styles["Normal"],
            )
        )

        # --------------------------------------------------
        # Build PDF
        # --------------------------------------------------

        document.build(
            story
        )

        pdf_bytes = (
            buffer.getvalue()
        )

        buffer.close()

        filename = (
            f"report_{report.metadata.report_id}.pdf"
        )

        return (
            pdf_bytes,
            filename,
        )

    # ==========================================================
    # Get Report
    # ==========================================================

    def get_report(
        self,
        report_id: int,
    ) -> Optional[ReportResponse]:
        """
        Retrieve one report from the database.
        """

        db = SessionLocal()

        try:

            report = (
                db.query(Report)
                .filter(
                    Report.id
                    == report_id
                )
                .first()
            )

            if report is None:

                return None

            patient = report.patient

            if patient is None:

                return None

            prediction_record = (
                db.query(Prediction)
                .filter(
                    Prediction.id
                    == report.prediction_id,

                    Prediction.patient_id
                    == patient.id,
                )
                .first()
            )

            prediction = (
                self._prediction_response(
                    prediction_record,
                    patient.id,
                )
            )

            return self._build_report_response(
                report_id=report.id,

                patient=patient,

                prediction=prediction,
            )

        finally:

            db.close()

    # ==========================================================
    # Get All Reports
    # ==========================================================

    def get_reports(
        self,
    ) -> ReportList:
        """
        Return all reports from the database.
        """

        db = SessionLocal()

        try:

            reports = (
                db.query(Report)
                .order_by(
                    Report.generated_at.desc()
                )
                .all()
            )

            result: List[
                ReportSummary
            ] = []

            for report in reports:

                patient = report.patient

                if patient is None:

                    continue

                result.append(
                    ReportSummary(

                        report_id=report.id,

                        patient_id=patient.id,

                        patient_name=(
                            f"{patient.first_name} "
                            f"{patient.last_name}"
                        ).strip(),

                        report_name=(
                            report.report_name
                        ),

                        generated_at=(
                            report.generated_at
                        ),
                    )
                )

            return ReportList(

                total_reports=len(
                    result
                ),

                reports=result,
            )

        finally:

            db.close()

    # ==========================================================
    # Get Patient Reports
    # ==========================================================

    def get_patient_reports(
        self,
        patient_id: int,
    ) -> List[ReportSummary]:
        """
        Return reports belonging to one patient.
        """

        db = SessionLocal()

        try:

            reports = (
                db.query(Report)
                .filter(
                    Report.patient_id
                    == patient_id
                )
                .order_by(
                    Report.generated_at.desc()
                )
                .all()
            )

            result = []

            for report in reports:

                patient = report.patient

                if patient is None:

                    continue

                result.append(
                    ReportSummary(

                        report_id=report.id,

                        patient_id=patient.id,

                        patient_name=(
                            f"{patient.first_name} "
                            f"{patient.last_name}"
                        ).strip(),

                        report_name=(
                            report.report_name
                        ),

                        generated_at=(
                            report.generated_at
                        ),
                    )
                )

            return result

        finally:

            db.close()

    # ==========================================================
    # Download Report
    # ==========================================================

    def download_report(
        self,
        report_id: int,
    ):
        """
        Return the stored PDF.

        If the PDF does not exist, regenerate it and save it.
        """

        db = SessionLocal()

        try:

            database_report = (
                db.query(Report)
                .filter(
                    Report.id
                    == report_id
                )
                .first()
            )

            if database_report is None:

                return None

            # --------------------------------------------------
            # Existing PDF
            # --------------------------------------------------

            if database_report.report_path:

                existing_path = Path(
                    database_report.report_path
                )

                if existing_path.exists():

                    return (
                        existing_path.read_bytes(),
                        existing_path.name,
                    )

            # --------------------------------------------------
            # Rebuild Report Response
            # --------------------------------------------------

            patient = (
                database_report.patient
            )

            if patient is None:

                return None

            prediction_record = (
                db.query(Prediction)
                .filter(
                    Prediction.id
                    == database_report.prediction_id,

                    Prediction.patient_id
                    == patient.id,
                )
                .first()
            )

            prediction = (
                self._prediction_response(
                    prediction_record,
                    patient.id,
                )
            )

            report_response = (
                self._build_report_response(
                    report_id=database_report.id,

                    patient=patient,

                    prediction=prediction,
                )
            )

            # --------------------------------------------------
            # Generate PDF
            # --------------------------------------------------

            pdf_bytes, filename = (
                self._generate_pdf(
                    report_response
                )
            )

            pdf_path = (
                REPORTS_DIR / filename
            )

            pdf_path.write_bytes(
                pdf_bytes
            )

            # --------------------------------------------------
            # Store Path
            # --------------------------------------------------

            database_report.report_path = (
                str(pdf_path)
            )

            db.commit()

            return (
                pdf_bytes,
                filename,
            )

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    # ==========================================================
    # Delete Report
    # ==========================================================

    def delete_report(
        self,
        report_id: int,
    ) -> Optional[
        DeleteReportResponse
    ]:
        """
        Delete a report from the database and its PDF file.
        """

        db = SessionLocal()

        try:

            report = (
                db.query(Report)
                .filter(
                    Report.id
                    == report_id
                )
                .first()
            )

            if report is None:

                return None

            # --------------------------------------------------
            # Delete PDF
            # --------------------------------------------------

            if report.report_path:

                pdf_path = Path(
                    report.report_path
                )

                if pdf_path.exists():

                    try:

                        pdf_path.unlink()

                    except OSError:

                        pass

            # --------------------------------------------------
            # Delete Database Record
            # --------------------------------------------------

            db.delete(
                report
            )

            db.commit()

            return DeleteReportResponse(

                message=(
                    f"Report {report_id} "
                    "deleted successfully."
                )
            )

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    # ==========================================================
    # Prediction Response Helper
    # ==========================================================

    def _prediction_response(
        self,
        prediction_record,
        patient_id: int,
    ) -> PredictionResponse:

        if prediction_record is None:

            return PredictionResponse(

                prediction_id=0,

                patient_id=patient_id,

                prediction="Prediction Pending",

                probability=0.0,

                confidence=0.0,

                risk_score=0.0,

                risk_level="Unknown",

                recommendation=(
                    "Prediction information "
                    "is not available."
                ),
            )

        return PredictionResponse(

            prediction_id=(
                prediction_record.id
            ),

            patient_id=(
                prediction_record.patient_id
            ),

            prediction=(
                prediction_record.prediction
            ),

            probability=(
                prediction_record.probability
            ),

            confidence=(
                prediction_record.confidence
            ),

            risk_score=(
                prediction_record.probability
                * 100
                if prediction_record.probability
                is not None
                else 0.0
            ),

            risk_level=(
                prediction_record.risk_level
            ),

            recommendation=(
                self._recommendation_text(
                    prediction_record.risk_level
                )
            ),
        )

    # ==========================================================
    # Recommendation Text
    # ==========================================================

    def _recommendation_text(
        self,
        risk_level: Optional[str],
    ) -> str:

        if not risk_level:

            return (
                "Please consult a qualified "
                "healthcare professional."
            )

        level = str(
            risk_level
        ).lower()

        if level == "high risk":

            return (
                "Neurological consultation "
                "is recommended."
            )

        if level == "moderate risk":

            return (
                "Further clinical evaluation "
                "is recommended."
            )

        if level == "medium risk":

            return (
                "Further clinical evaluation "
                "is recommended."
            )

        if level == "low risk":

            return (
                "Continue healthy habits and "
                "regular medical evaluation."
            )

        return (
            "Please review the result with "
            "a qualified healthcare professional."
        )

    # ==========================================================
    # Recommendations
    # ==========================================================

    def _recommendations(
        self,
    ) -> List[RecommendationItem]:

        return [

            RecommendationItem(

                title="Lifestyle",

                description=(
                    "Maintain regular physical "
                    "activity and healthy sleep habits."
                ),
            ),

            RecommendationItem(

                title="Diet",

                description=(
                    "Maintain a balanced diet including "
                    "fruits, vegetables, and whole grains."
                ),
            ),
        ]

    # ==========================================================
    # Exercises
    # ==========================================================

    def _exercises(
        self,
    ) -> List[ExerciseItem]:

        return [

            ExerciseItem(

                name="Walking",

                duration="30 minutes",

                frequency="5 days/week",

                description=(
                    "Moderate walking as appropriate "
                    "for the individual's condition."
                ),
            ),

            ExerciseItem(

                name="Balance Training",

                duration="20 minutes",

                frequency="3 days/week",

                description=(
                    "Balance exercises may help support "
                    "mobility and stability."
                ),
            ),
        ]

    # ==========================================================
    # Medication
    # ==========================================================

    def _medication(
        self,
    ) -> List[MedicationItem]:

        return [

            MedicationItem(

                title="Medication Guidance",

                description=(
                    "Take medications only as prescribed "
                    "by your healthcare professional."
                ),
            ),

            MedicationItem(

                title="Medication Safety",

                description=(
                    "Never start, stop, or change medication "
                    "without professional medical advice."
                ),
            ),
        ]


# ==========================================================
# Shared Report Service
# ==========================================================

report_service = ReportService()
