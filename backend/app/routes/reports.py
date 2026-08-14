from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from app.dependencies import get_current_user

from app.schemas.report import (
    ReportRequest,
    ReportResponse,
)

from app.services.report_service import report_service


# ==========================================================
# Router
# ==========================================================

router = APIRouter(
    tags=["Reports"]
)


# ==========================================================
# Generate Report
# ==========================================================

@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_report(
    request: ReportRequest,
    current_user=Depends(get_current_user),
):
    """
    Generate a patient report manually.
    """

    try:

        report = report_service.generate_report(
            request=request
        )

        return report

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )


# ==========================================================
# Get All Reports
# ==========================================================

@router.get(
    "/",
)
def get_reports(
    current_user=Depends(get_current_user),
):
    """
    Return all generated reports.
    """

    return report_service.get_reports()


# ==========================================================
# Get Patient Reports
# ==========================================================

@router.get(
    "/patient/{patient_id}",
)
def get_patient_reports(
    patient_id: int,
    current_user=Depends(get_current_user),
):
    """
    Return all reports belonging to a patient.
    """

    return report_service.get_patient_reports(
        patient_id=patient_id
    )


# ==========================================================
# Download Report
# ==========================================================

@router.get(
    "/{report_id}/download",
)
def download_report(
    report_id: int,
    current_user=Depends(get_current_user),
):
    """
    Generate and download the report PDF.
    """

    result = report_service.download_report(
        report_id=report_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    pdf_bytes, filename = result

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


# ==========================================================
# Get Report By ID
# ==========================================================

@router.get(
    "/{report_id}",
)
def get_report(
    report_id: int,
    current_user=Depends(get_current_user),
):
    """
    Retrieve one report by ID.
    """

    report = report_service.get_report(
        report_id=report_id
    )

    if report is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return report


# ==========================================================
# Delete Report
# ==========================================================

@router.delete(
    "/{report_id}",
)
def delete_report(
    report_id: int,
    current_user=Depends(get_current_user),
):
    """
    Delete a report by ID.
    """

    result = report_service.delete_report(
        report_id=report_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return result
