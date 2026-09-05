from collections import Counter
from datetime import datetime

from app.database.database import SessionLocal

from app.database.models import (
    Patient,
    Prediction,
    Report,
)

from app.schemas.analytics import (
    DashboardAnalytics,
    PredictionAnalytics,
    PatientAnalytics,
    MonthlyTrend,
    AgeDistribution,
    GenderDistribution,
    RiskDistribution,
    DiseaseDistribution,
    RecentPrediction,
    AnalyticsSummary,
)


class AnalyticsService:
    """
    Service for database-based analytics.
    """

    # ==========================================================
    # Database Helper
    # ==========================================================

    def _get_session(self):
        """
        Create a database session.
        """

        return SessionLocal()


    # ==========================================================
    # Patient Name Helper
    # ==========================================================

    @staticmethod
    def _patient_name(patient):
        """
        Safely create a patient display name.
        """

        if patient is None:
            return "Unknown Patient"

        first_name = (
            patient.first_name
            or ""
        ).strip()

        last_name = (
            patient.last_name
            or ""
        ).strip()

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

        return (
            full_name
            or f"Patient {patient.id}"
        )


    # ==========================================================
    # Prediction Type Helper
    # ==========================================================

    @staticmethod
    def _is_parkinson(prediction):
        """
        Determine whether a prediction represents
        a Parkinson classification.
        """

        value = str(
            prediction.prediction
            or ""
        ).strip().lower()

        return (
            "parkinson" in value
        )


    # ==========================================================
    # Risk Score Helper
    # ==========================================================

    @staticmethod
    def _risk_score(prediction):
        """
        Convert stored probability into percentage.

        Supports both:
        - 0.0 to 1.0 probability
        - already stored percentages
        """

        value = (
            prediction.probability
            or 0.0
        )

        try:

            value = float(value)

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        if 0 <= value <= 1:

            value *= 100

        return value


    # ==========================================================
    # Dashboard Metrics
    # ==========================================================

    def dashboard(
        self,
    ) -> DashboardAnalytics:
        """
        Calculate dashboard metrics directly
        from the database.
        """

        db = self._get_session()

        try:

            total_patients = (
                db.query(Patient).count()
            )

            total_predictions = (
                db.query(Prediction).count()
            )

            total_reports = (
                db.query(Report).count()
            )

            predictions = (
                db.query(Prediction).all()
            )

            healthy_cases = 0
            parkinson_cases = 0

            high_risk_cases = 0
            medium_risk_cases = 0
            low_risk_cases = 0


            for prediction in predictions:

                if self._is_parkinson(
                    prediction
                ):

                    parkinson_cases += 1

                else:

                    healthy_cases += 1


                risk_level = str(
                    prediction.risk_level
                    or ""
                ).strip().lower()


                if (
                    "high" in risk_level
                ):

                    high_risk_cases += 1


                elif (
                    "medium" in risk_level
                ):

                    medium_risk_cases += 1


                elif (
                    "low" in risk_level
                ):

                    low_risk_cases += 1


            return DashboardAnalytics(

                total_patients=
                    total_patients,

                total_predictions=
                    total_predictions,

                total_reports=
                    total_reports,

                healthy_cases=
                    healthy_cases,

                parkinson_cases=
                    parkinson_cases,

                high_risk_cases=
                    high_risk_cases,

                medium_risk_cases=
                    medium_risk_cases,

                low_risk_cases=
                    low_risk_cases,
            )

        finally:

            db.close()


    # ==========================================================
    # Prediction Statistics
    # ==========================================================

    def prediction_statistics(
        self,
    ) -> PredictionAnalytics:
        """
        Calculate prediction statistics
        directly from the database.
        """

        db = self._get_session()

        try:

            predictions = (
                db.query(Prediction).all()
            )

            total_predictions = len(
                predictions
            )

            healthy_predictions = 0
            parkinson_predictions = 0

            confidence_values = []
            risk_values = []


            for prediction in predictions:

                if self._is_parkinson(
                    prediction
                ):

                    parkinson_predictions += 1

                else:

                    healthy_predictions += 1


                if (
                    prediction.confidence
                    is not None
                ):

                    confidence_values.append(
                        float(
                            prediction.confidence
                        )
                    )


                risk_values.append(
                    self._risk_score(
                        prediction
                    )
                )


            average_confidence = (

                sum(confidence_values)
                / len(confidence_values)

                if confidence_values

                else 0.0
            )


            average_risk_score = (

                sum(risk_values)
                / len(risk_values)

                if risk_values

                else 0.0
            )


            return PredictionAnalytics(

                total_predictions=
                    total_predictions,

                healthy_predictions=
                    healthy_predictions,

                parkinson_predictions=
                    parkinson_predictions,

                average_confidence=
                    round(
                        average_confidence,
                        2,
                    ),

                average_risk_score=
                    round(
                        average_risk_score,
                        2,
                    ),
            )

        finally:

            db.close()


    # ==========================================================
    # Patient Statistics
    # ==========================================================

    def patient_statistics(
        self,
    ) -> PatientAnalytics:
        """
        Calculate patient statistics
        directly from the database.
        """

        db = self._get_session()

        try:

            patients = (
                db.query(Patient).all()
            )

            total_patients = len(
                patients
            )

            male_patients = 0
            female_patients = 0
            other_patients = 0

            ages = []


            for patient in patients:

                gender = str(
                    patient.gender
                    or ""
                ).strip().lower()


                if gender == "male":

                    male_patients += 1


                elif gender == "female":

                    female_patients += 1


                else:

                    other_patients += 1


                if (
                    patient.age
                    is not None
                ):

                    try:

                        ages.append(
                            float(
                                patient.age
                            )
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        pass


            average_age = (

                sum(ages)
                / len(ages)

                if ages

                else 0.0
            )


            return PatientAnalytics(

                total_patients=
                    total_patients,

                male_patients=
                    male_patients,

                female_patients=
                    female_patients,

                other_patients=
                    other_patients,

                average_age=
                    round(
                        average_age,
                        1,
                    ),
            )

        finally:

            db.close()


    # ==========================================================
    # Monthly Trend
    # ==========================================================

    def monthly_trend(
        self,
    ):
        """
        Calculate monthly prediction trend.
        """

        db = self._get_session()

        try:

            predictions = (
                db.query(Prediction)
                .order_by(
                    Prediction.created_at.asc()
                )
                .all()
            )


            counts = Counter()


            for prediction in predictions:

                if (
                    prediction.created_at
                    is None
                ):

                    continue


                key = (
                    prediction.created_at.year,
                    prediction.created_at.month,
                )


                counts[key] += 1


            results = []


            for (
                year,
                month,
            ), count in sorted(
                counts.items()
            ):

                month_name = datetime(
                    year,
                    month,
                    1,
                ).strftime(
                    "%B %Y"
                )


                results.append(

                    MonthlyTrend(

                        month=
                            month_name,

                        predictions=
                            count,
                    )
                )


            return results

        finally:

            db.close()


    # ==========================================================
    # Age Distribution
    # ==========================================================

    def age_distribution(
        self,
    ):
        """
        Calculate patient age distribution.
        """

        db = self._get_session()

        try:

            patients = (
                db.query(Patient).all()
            )


            distribution = Counter()


            for patient in patients:

                if (
                    patient.age
                    is None
                ):

                    continue


                age = patient.age


                if age <= 50:

                    group = "40-50"

                elif age <= 60:

                    group = "51-60"

                elif age <= 70:

                    group = "61-70"

                elif age <= 80:

                    group = "71-80"

                else:

                    group = "81+"


                distribution[
                    group
                ] += 1


            groups = [

                "40-50",

                "51-60",

                "61-70",

                "71-80",

                "81+",
            ]


            return [

                AgeDistribution(

                    age_group=
                        group,

                    count=
                        distribution.get(
                            group,
                            0,
                        ),
                )

                for group in groups

                if distribution.get(
                    group,
                    0,
                ) > 0
            ]

        finally:

            db.close()


    # ==========================================================
    # Gender Distribution
    # ==========================================================

    def gender_distribution(
        self,
    ):
        """
        Calculate patient gender distribution.
        """

        db = self._get_session()

        try:

            patients = (
                db.query(Patient).all()
            )


            distribution = Counter()


            for patient in patients:

                gender = str(
                    patient.gender
                    or ""
                ).strip().lower()


                if gender == "male":

                    label = "Male"

                elif gender == "female":

                    label = "Female"

                else:

                    label = "Other"


                distribution[
                    label
                ] += 1


            return [

                GenderDistribution(
                    gender="Male",
                    count=distribution.get(
                        "Male",
                        0,
                    ),
                ),

                GenderDistribution(
                    gender="Female",
                    count=distribution.get(
                        "Female",
                        0,
                    ),
                ),

                GenderDistribution(
                    gender="Other",
                    count=distribution.get(
                        "Other",
                        0,
                    ),
                ),
            ]

        finally:

            db.close()


    # ==========================================================
    # Risk Distribution
    # ==========================================================

    def risk_distribution(
        self,
    ):
        """
        Calculate prediction risk distribution.
        """

        db = self._get_session()

        try:

            predictions = (
                db.query(Prediction).all()
            )


            distribution = Counter()


            for prediction in predictions:

                risk_level = str(
                    prediction.risk_level
                    or ""
                ).strip()


                if risk_level:

                    distribution[
                        risk_level
                    ] += 1


            return [

                RiskDistribution(
                    risk_level="Low Risk",
                    count=distribution.get(
                        "Low Risk",
                        0,
                    ),
                ),

                RiskDistribution(
                    risk_level="Medium Risk",
                    count=distribution.get(
                        "Medium Risk",
                        0,
                    ),
                ),

                RiskDistribution(
                    risk_level="High Risk",
                    count=distribution.get(
                        "High Risk",
                        0,
                    ),
                ),
            ]

        finally:

            db.close()


    # ==========================================================
    # Disease Distribution
    # ==========================================================

    def disease_distribution(
        self,
    ):
        """
        Calculate Healthy vs Parkinson distribution.
        """

        db = self._get_session()

        try:

            predictions = (
                db.query(Prediction).all()
            )


            healthy = 0
            parkinson = 0


            for prediction in predictions:

                if self._is_parkinson(
                    prediction
                ):

                    parkinson += 1

                else:

                    healthy += 1


            return [

                DiseaseDistribution(
                    label="Healthy",
                    count=healthy,
                ),

                DiseaseDistribution(
                    label="Parkinson",
                    count=parkinson,
                ),
            ]

        finally:

            db.close()


    # ==========================================================
    # Recent Predictions
    # ==========================================================

    def recent_predictions(
        self,
    ):
        """
        Return recent predictions.
        """

        db = self._get_session()

        try:

            predictions = (

                db.query(Prediction)

                .order_by(
                    Prediction.created_at.desc()
                )

                .limit(10)

                .all()
            )


            results = []


            for prediction in predictions:

                results.append(

                    RecentPrediction(

                        prediction_id=
                            prediction.id,

                        patient_name=
                            self._patient_name(
                                prediction.patient
                            ),

                        prediction=
                            str(
                                prediction.prediction
                                or "Unknown"
                            ),

                        confidence=
                            float(
                                prediction.confidence
                                or 0.0
                            ),

                        risk_level=
                            str(
                                prediction.risk_level
                                or "Unknown"
                            ),

                        created_at=(

                            prediction.created_at.isoformat()

                            if prediction.created_at

                            else ""
                        ),
                    )
                )


            return results

        finally:

            db.close()


    # ==========================================================
    # Complete Analytics Summary
    # ==========================================================

    def analytics_summary(
        self,
    ) -> AnalyticsSummary:
        """
        Return complete database-based analytics.
        """

        return AnalyticsSummary(

            dashboard=
                self.dashboard(),

            prediction=
                self.prediction_statistics(),

            patient=
                self.patient_statistics(),

            monthly_trend=
                self.monthly_trend(),

            age_distribution=
                self.age_distribution(),

            gender_distribution=
                self.gender_distribution(),

            risk_distribution=
                self.risk_distribution(),

            disease_distribution=
                self.disease_distribution(),

            recent_predictions=
                self.recent_predictions(),
        )


    # ==========================================================
    # Compatibility Alias
    # ==========================================================

    def summary(
        self,
    ) -> AnalyticsSummary:
        """
        Compatibility method.
        """

        return (
            self.analytics_summary()
        )
