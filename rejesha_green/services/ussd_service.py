from sqlalchemy.orm import Session
from fastapi.responses import PlainTextResponse

from rejesha_green.models.incident import ActivityType
from rejesha_green.models.forest_zone import ForestZone
from rejesha_green.schemas.incidents import IncidentReportCreate
from rejesha_green.services.incident_service import create_incident_report


def handle_ussd(
    db: Session,
    text: str
):
    text_segments = text.split("*") if text else []

    if len(text_segments) == 0:
        return PlainTextResponse(
            "CON Welcome to Rejesha Green.\n"
            "1. Report Incident\n"
            "2. Access Resources"
        )

    if len(text_segments) == 1:

        if text_segments[0] == "1":
            return PlainTextResponse(
                "CON Select Incident Type:\n"
                "1. Charcoal Burning\n"
                "2. Logging\n"
                "3. Poaching\n"
                "4. Others"
            )

        if text_segments[0] == "2":
            return PlainTextResponse(
                "END Resources are currently unavailable."
            )

        return PlainTextResponse(
            "END Invalid selection."
        )


    incident_types = {
        "1": ActivityType.Charcoal_Burning,
        "2": ActivityType.Logging,
        "3": ActivityType.Poaching,
        "4": ActivityType.Others,
    }


    if len(text_segments) == 2:

        selected_type = incident_types.get(text_segments[1])

        if selected_type is None:
            return PlainTextResponse(
                "END Invalid incident type."
            )


        zones = (
            db.query(ForestZone)
            .filter(ForestZone.is_available.is_(True))
            .limit(5)
            .all()
        )


        if not zones:
            return PlainTextResponse(
                "END No forest zones available."
            )


        response = "CON Select Forest Zone:\n"


        for index, zone in enumerate(zones, start=1):
            response += (
                f"{index}. "
                f"{zone.cfa_name} - {zone.block_name}\n"
            )


        return PlainTextResponse(
            response.rstrip()
        )



    if len(text_segments) == 3:

        selected_type = incident_types.get(text_segments[1])

        if selected_type is None:
            return PlainTextResponse(
                "END Invalid incident type."
            )


        zones = (
            db.query(ForestZone)
            .filter(ForestZone.is_available.is_(True))
            .limit(5)
            .all()
        )


        try:
            zone_index = int(text_segments[2]) - 1

        except ValueError:
            return PlainTextResponse(
                "END Invalid zone selection."
            )


        if zone_index < 0 or zone_index >= len(zones):
            return PlainTextResponse(
                "END Invalid zone selection."
            )


        selected_zone = zones[zone_index]


        report_data = IncidentReportCreate(
            zone_id=selected_zone.zone_id,
            incident_type=selected_type
        )


        create_incident_report(
            db,
            report_data
        )


        return PlainTextResponse(
            "END Incident submitted successfully!"
        )


    return PlainTextResponse(
        "END Invalid USSD request."
    )