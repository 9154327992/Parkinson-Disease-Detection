from collections import Counter, defaultdict
from typing import List

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

from app.services.prediction_service import (
    PredictionService,
)


class AnalyticsService:
    """
    Service for analytics and dashboard data.
    """

    def __init__(self):
        """
        Use the shared PredictionService storage.
        """

        self.prediction_service = PredictionService()

    # ==========================================================
    # Internal Records
    # ==========================================================

    def _records(self):
        """
        Return all actual prediction records.
        """

        return PredictionService.predictions

    # ==========================================================
    # Dashboard Metrics
    # ==========================================================

    def dashboard(
        self,
    ) -> DashboardAnalytics:
        """
        Calculate dashboard metrics from actual predictions.
        """

        records = self._records()

        total_predictions = len(
            records
        )

        # ------------------------------------------------------
        # Unique Patients
        # ------------------------------------------------------

        patients = set()

        for record in records.values():

            patients.add(
                (
                    record["patient_name"],
                    record["age"],
                    record["gender"],
                )
            )

        total_patients = len(
            patients
        )

        # ------------------------------------------------------
        # Prediction Counts
        # ------------------------------------------------------

        healthy_cases = 0

        parkinson_cases = 0

        high_risk_cases = 0

        medium_risk_cases = 0

        low_risk_cases = 0

        for record in records.values():

            response = record["response"]

            if response.prediction_value == 1:

                parkinson_cases += 1

            else:

                healthy_cases += 1

            if response.risk_level == "High Risk":

                high_risk_cases += 1

            elif response.risk_level == "Medium Risk":

                medium_risk_cases += 1

            elif response.risk_level == "Low Risk":

                low_risk_cases += 1

        return DashboardAnalytics(

            total_patients=total_patients,

            total_predictions=total_predictions,

            healthy_cases=healthy_cases,

            parkinson_cases=parkinson_cases,

            high_risk_cases=high_risk_cases,

            medium_risk_cases=medium_risk_cases,

            low_risk_cases=low_risk_cases,
        )

    # ==========================================================
    # Prediction Statistics
    # ==========================================================

    def prediction_statistics(
        self,
    ) -> PredictionAnalytics:
        """
        Calculate prediction statistics from actual records.
        """

        records = self._records()

        total_predictions = len(
            records
        )

        healthy_predictions = 0

        parkinson_predictions = 0

        confidence_values = []

        risk_values = []

        for record in records.values():

            response = record["response"]

            confidence_values.append(
                response.confidence
            )

            risk_values.append(
                response.risk_score
            )

            if response.prediction_value == 1:

                parkinson_predictions += 1

            else:

                healthy_predictions += 1

        # ------------------------------------------------------
        # Average Confidence
        # ------------------------------------------------------

        if confidence_values:

            average_confidence = (
                sum(confidence_values)
                / len(confidence_values)
            )

        else:

            average_confidence = 0.0

        # ------------------------------------------------------
        # Average Risk
        # ------------------------------------------------------

        if risk_values:

            average_risk_score = (
                sum(risk_values)
                / len(risk_values)
            )

        else:

            average_risk_score = 0.0

        return PredictionAnalytics(

            total_predictions=total_predictions,

            healthy_predictions=healthy_predictions,

            parkinson_predictions=parkinson_predictions,

            average_confidence=round(
                average_confidence,
                2,
            ),

            average_risk_score=round(
                average_risk_score,
                2,
            ),
        )

    # ==========================================================
    # Patient Statistics
    # ==========================================================

    def patient_statistics(
        self,
    ) -> PatientAnalytics:
        """
        Calculate patient demographics from actual records.
        """

        records = self._records()

        patients = {}

        for record in records.values():

            key = (
                record["patient_name"],
                record["age"],
                record["gender"],
            )

            patients[key] = {
                "name": record["patient_name"],
                "age": record["age"],
                "gender": record["gender"],
            }

        patient_list = list(
            patients.values()
        )

        total_patients = len(
            patient_list
        )

        male_patients = sum(
            1
            for patient in patient_list
            if patient["gender"].lower()
            == "male"
        )

        female_patients = sum(
            1
            for patient in patient_list
            if patient["gender"].lower()
            == "female"
        )

        other_patients = (
            total_patients
            - male_patients
            - female_patients
        )

        ages = [
            patient["age"]
            for patient in patient_list
            if isinstance(
                patient["age"],
                (int, float),
            )
        ]

        if ages:

            average_age = (
                sum(ages)
                / len(ages)
            )

        else:

            average_age = 0.0

        return PatientAnalytics(

            total_patients=total_patients,

            male_patients=male_patients,

            female_patients=female_patients,

            other_patients=other_patients,

            average_age=round(
                average_age,
                1,
            ),
        )

    # ==========================================================
    # Monthly Trend
    # ==========================================================

    def monthly_trend(
        self,
    ) -> List[MonthlyTrend]:
        """
        Calculate monthly prediction counts from actual records.
        """

        records = self._records()

        monthly_counts = defaultdict(
            int
        )

        for record in records.values():

            created_at = (
                record["response"].created_at
            )

            month_key = (
                created_at.year,
                created_at.month,
            )

            monthly_counts[
                month_key
            ] += 1

        # ------------------------------------------------------
        # Sort chronologically
        # ------------------------------------------------------

        sorted_months = sorted(
            monthly_counts.keys()
        )

        return [

            MonthlyTrend(

                month=(
                    self._month_name(
                        month_number
                    )
                ),

                predictions=monthly_counts[
                    (year, month_number)
                ],
            )

            for year, month_number
            in sorted_months
        ]

    # ==========================================================
    # Month Name
    # ==========================================================

    def _month_name(
        self,
        month_number: int,
    ) -> str:
        """
        Convert month number to month name.
        """

        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        return months[
            month_number - 1
        ]

    # ==========================================================
    # Age Distribution
    # ==========================================================

    def age_distribution(
        self,
    ) -> List[AgeDistribution]:
        """
        Calculate age distribution from actual patients.
        """

        records = self._records()

        patients = {}

        for record in records.values():

            key = (
                record["patient_name"],
                record["age"],
                record["gender"],
            )

            patients[key] = record

        distribution = Counter()

        for record in patients.values():

            age = record["age"]

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

            distribution[group] += 1

        ordered_groups = [
            "40-50",
            "51-60",
            "61-70",
            "71-80",
            "81+",
        ]

        return [

            AgeDistribution(

                age_group=group,

                count=distribution.get(
                    group,
                    0,
                ),
            )

            for group in ordered_groups

            if distribution.get(
                group,
                0,
            ) > 0
        ]

    # ==========================================================
    # Gender Distribution
    # ==========================================================

    def gender_distribution(
        self,
    ) -> List[GenderDistribution]:
        """
        Calculate gender distribution from actual patients.
        """

        records = self._records()

        patients = {}

        for record in records.values():

            key = (
                record["patient_name"],
                record["age"],
                record["gender"],
            )

            patients[key] = record

        distribution = Counter()

        for record in patients.values():

            gender = record["gender"]

            if gender.lower() == "male":

                label = "Male"

            elif gender.lower() == "female":

                label = "Female"

            else:

                label = "Other"

            distribution[label] += 1

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

    # ==========================================================
    # Risk Distribution
    # ==========================================================

    def risk_distribution(
        self,
    ) -> List[RiskDistribution]:
        """
        Calculate risk distribution from actual predictions.
        """

        records = self._records()

        distribution = Counter()

        for record in records.values():

            risk_level = (
                record["response"].risk_level
            )

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

    # ==========================================================
    # Disease Distribution
    # ==========================================================

    def disease_distribution(
        self,
    ) -> List[DiseaseDistribution]:
        """
        Calculate disease distribution from actual predictions.
        """

        records = self._records()

        healthy = 0

        parkinson = 0

        for record in records.values():

            response = record["response"]

            if response.prediction_value == 1:

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

    # ==========================================================
    # Recent Predictions
    # ==========================================================

    def recent_predictions(
        self,
    ) -> List[RecentPrediction]:
        """
        Return actual recent predictions.
        """

        records = list(
            self._records().values()
        )

        records.sort(
            key=lambda record:
                record["response"].created_at,
            reverse=True,
        )

        recent = records[:10]

        return [

            RecentPrediction(

                prediction_id=(
                    record["response"].prediction_id
                ),

                patient_name=(
                    record["patient_name"]
                ),

                prediction=(
                    record["response"].prediction
                ),

                confidence=(
                    record["response"].confidence
                ),

                risk_level=(
                    record["response"].risk_level
                ),

                created_at=(
                    record["response"]
                    .created_at
                    .isoformat()
                ),
            )

            for record in recent
        ]

    # ==========================================================
    # Complete Analytics
    # ==========================================================

    def analytics_summary(
        self,
    ) -> AnalyticsSummary:
        """
        Return complete analytics based on actual records.
        """

        return AnalyticsSummary(

            dashboard=self.dashboard(),

            prediction=self.prediction_statistics(),

            patient=self.patient_statistics(),

            monthly_trend=self.monthly_trend(),

            age_distribution=self.age_distribution(),

            gender_distribution=self.gender_distribution(),

            risk_distribution=self.risk_distribution(),

            disease_distribution=self.disease_distribution(),

            recent_predictions=self.recent_predictions(),
        )

    # ==========================================================
    # Compatibility Alias
    # ==========================================================

    def summary(
        self,
    ) -> AnalyticsSummary:
        """
        Compatibility method for existing routes.
        """

        return self.analytics_summary()
