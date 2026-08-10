from datetime import datetime
from typing import Dict, List, Optional

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
    ReportDownload,
    ReportList,
    DeleteReportResponse,
)

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)


class ReportService:
    """
    Handles patient report generation.

    Reports are currently stored in memory.

    A shared service instance is created at the bottom of this
    file so prediction.py and reports.py use the SAME report
    storage.
    """

    def __init__(self):
        """
        Initialize report service.
        """

        # --------------------------------------------------
        # Report storage
        # --------------------------------------------------

        self._reports: Dict[int, ReportResponse] = {}

        # --------------------------------------------------
        # Report ID counter
        # --------------------------------------------------

        self._next_report_id = 1

    # ==========================================================
    # Generate Report From Prediction
    # ==========================================================

    def generate_from_prediction(
        self,
        request: PredictionRequest,
        prediction: PredictionResponse,
    ) -> ReportResponse:
        """
        Automatically generate a report from a completed
        prediction.

        Uses the actual patient information and the actual
        prediction result.
        """

        # --------------------------------------------------
        # Generate report ID
        # --------------------------------------------------

        report_id = self._next_report_id

        self._next_report_id += 1

        # --------------------------------------------------
        # Create report
        # --------------------------------------------------

        report = ReportResponse(

            metadata=ReportMetadata(
                report_id=report_id,
                report_name=(
                    "Parkinson Disease Assessment Report"
                ),
                report_type="PDF",
                generated_by="System",
                generated_at=datetime.utcnow(),
                version="1.0.0",
            ),

            # --------------------------------------------------
            # Actual patient information
            # --------------------------------------------------

            patient=ReportPatient(
                patient_id=prediction.patient_id,
                full_name=request.patient_name,
                age=request.age,
                gender=request.gender,
                medical_history=None,
            ),

            # --------------------------------------------------
            # Actual prediction information
            # --------------------------------------------------

            prediction=PredictionSummary(
                prediction=prediction.prediction,
                confidence=prediction.confidence,
                risk_score=prediction.risk_score,
                risk_level=prediction.risk_level,
                recommendation=prediction.recommendation,
            ),

            # --------------------------------------------------
            # Additional report sections
            # --------------------------------------------------

            recommendations=self._recommendations(),

            exercises=self._exercises(),

            medication=self._medication(),

            follow_up=FollowUpPlan(
                next_visit=(
                    "As recommended by a healthcare professional"
                ),
                specialist="Neurologist",
                notes=(
                    "Review the prediction results with "
                    "a qualified healthcare professional."
                ),
            ),

            doctor_notes=None,
        )

        # --------------------------------------------------
        # Save report
        # --------------------------------------------------

        self._reports[report_id] = report

        return report

    # ==========================================================
    # Generate Manual Report
    # ==========================================================

    def generate_report(
        self,
        request: ReportRequest,
    ) -> ReportResponse:
        """
        Generate a report manually.

        This method is retained for the POST /reports/
        endpoint.
        """

        # --------------------------------------------------
        # Generate report ID
        # --------------------------------------------------

        report_id = self._next_report_id

        self._next_report_id += 1

        # --------------------------------------------------
        # Recommendations
        # --------------------------------------------------

        recommendations = (
            self._recommendations()
            if request.include_recommendations
            else []
        )

        # --------------------------------------------------
        # Exercises
        # --------------------------------------------------

        exercises = (
            self._exercises()
            if request.include_exercises
            else []
        )

        # --------------------------------------------------
        # Medication
        # --------------------------------------------------

        medication = (
            self._medication()
            if request.include_medication
            else []
        )

        # --------------------------------------------------
        # Follow-up
        # --------------------------------------------------

        if request.include_follow_up:

            follow_up = FollowUpPlan(
                next_visit=(
                    "As recommended by a healthcare professional"
                ),
                specialist="Neurologist",
                notes=(
                    "Review the report with a "
                    "qualified healthcare professional."
                ),
            )

        else:

            follow_up = FollowUpPlan(
                next_visit="Not included",
                specialist="Not specified",
                notes=(
                    "Follow-up section was not requested."
                ),
            )

        # --------------------------------------------------
        # Create report
        # --------------------------------------------------

        report = ReportResponse(

            metadata=ReportMetadata(
                report_id=report_id,
                report_name=(
                    "Parkinson Disease Assessment Report"
                ),
                report_type="PDF",
                generated_by="System",
                generated_at=datetime.utcnow(),
                version="1.0.0",
            ),

            patient=ReportPatient(
                patient_id=request.patient_id,
                full_name="Patient",
                age=0,
                gender="Not Specified",
                medical_history=None,
            ),

            prediction=PredictionSummary(
                prediction="Prediction Pending",
                confidence=0.0,
                risk_score=0.0,
                risk_level="Unknown",
                recommendation=(
                    "Prediction information should be "
                    "provided from the prediction record."
                ),
            ),

            recommendations=recommendations,

            exercises=exercises,

            medication=medication,

            follow_up=follow_up,

            doctor_notes=request.doctor_notes,
        )

        # --------------------------------------------------
        # Save report
        # --------------------------------------------------

        self._reports[report_id] = report

        return report

    # ==========================================================
    # Get Report
    # ==========================================================

    def get_report(
        self,
        report_id: int,
    ) -> Optional[ReportResponse]:
        """
        Retrieve one report by ID.
        """

        return self._reports.get(
            report_id
        )

    # ==========================================================
    # Get All Reports
    # ==========================================================

    def get_reports(
        self,
    ) -> ReportList:
        """
        Return all generated reports.
        """

        reports: List[ReportSummary] = []

        for report_id, report in self._reports.items():

            reports.append(
                ReportSummary(
                    report_id=report_id,

                    patient_id=(
                        report.patient.patient_id
                    ),

                    patient_name=(
                        report.patient.full_name
                    ),

                    report_name=(
                        report.metadata.report_name
                    ),

                    generated_at=(
                        report.metadata.generated_at
                    ),
                )
            )

        return ReportList(
            total_reports=len(reports),
            reports=reports,
        )

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

        reports: List[ReportSummary] = []

        for report_id, report in self._reports.items():

            if report.patient.patient_id != patient_id:

                continue

            reports.append(
                ReportSummary(
                    report_id=report_id,

                    patient_id=(
                        report.patient.patient_id
                    ),

                    patient_name=(
                        report.patient.full_name
                    ),

                    report_name=(
                        report.metadata.report_name
                    ),

                    generated_at=(
                        report.metadata.generated_at
                    ),
                )
            )

        return reports

    # ==========================================================
    # Download Report Information
    # ==========================================================

    def download_report(
        self,
        report_id: int,
    ) -> Optional[ReportDownload]:
        """
        Return download information for a report.

        Actual PDF generation is not implemented yet.
        """

        if report_id not in self._reports:

            return None

        return ReportDownload(
            report_id=report_id,
            filename=f"report_{report_id}.pdf",
            download_url=(
                f"/reports/{report_id}/download"
            ),
            file_type="pdf",
            file_size="Not generated",
        )

    # ==========================================================
    # Delete Report
    # ==========================================================

    def delete_report(
        self,
        report_id: int,
    ) -> Optional[DeleteReportResponse]:
        """
        Delete a report by ID.
        """

        if report_id not in self._reports:

            return None

        del self._reports[
            report_id
        ]

        return DeleteReportResponse(
            message=(
                f"Report {report_id} "
                "deleted successfully."
            )
        )

    # ==========================================================
    # Recommendation Section
    # ==========================================================

    def _recommendations(
        self,
    ) -> List[RecommendationItem]:
        """
        Return general educational recommendations.
        """

        return [

            RecommendationItem(
                title="Lifestyle",
                description=(
                    "Maintain regular physical activity "
                    "and healthy sleep habits."
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
    # Exercise Section
    # ==========================================================

    def _exercises(
        self,
    ) -> List[ExerciseItem]:
        """
        Return general educational exercise information.
        """

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
    # Medication Section
    # ==========================================================

    def _medication(
        self,
    ) -> List[MedicationItem]:
        """
        Return educational medication guidance.

        This does not prescribe medication.
        """

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
