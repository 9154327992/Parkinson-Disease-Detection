"""
Report API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.dependencies import get_current_user

from app.schemas.report import (
    ReportRequest,
    ReportResponse,
)

from app.services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

report_service = ReportService()


# ==========================================================
# Generate Report
# ==========================================================

@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_report(
    request: ReportRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate a patient report.
    """

    try:

        return report_service.generate_report(
            request=request,
            user=current_user
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================================
# Get All Reports
# ==========================================================

@router.get(
    "/",
    response_model=list[ReportResponse]
)
def get_reports(
    current_user=Depends(get_current_user)
):
    """
    Return all reports.
    """

    return report_service.get_reports()


# ==========================================================
# Get Report
# ==========================================================

@router.get(
    "/{report_id}",
    response_model=ReportResponse
)
def get_report(
    report_id: int,
    current_user=Depends(get_current_user)
):
    """
    Return a report by ID.
    """

    report = report_service.get_report(report_id)

    if report is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found."
        )

    return report


# ==========================================================
# Download Report
# ==========================================================

@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    current_user=Depends(get_current_user)
):
    """
    Download PDF report.
    """

    pdf_path = report_service.download(report_id)

    if pdf_path is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found."
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"report_{report_id}.pdf"
    )


# ==========================================================
# Patient Reports
# ==========================================================

@router.get("/patient/{patient_id}")
def patient_reports(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Return all reports for a patient.
    """

    return report_service.patient_reports(
        patient_id
    )


# ==========================================================
# Delete Report
# ==========================================================

@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    current_user=Depends(get_current_user)
):
    """
    Delete a report.
    """

    deleted = report_service.delete_report(
        report_id
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found."
        )

    return {
        "message": "Report deleted successfully."
    }
