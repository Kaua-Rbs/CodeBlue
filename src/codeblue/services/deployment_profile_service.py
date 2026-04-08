from __future__ import annotations

from datetime import date
from typing import Final

from codeblue.domain.knowledge_runtime_models import DeploymentProfile

MONTH_ORDER: Final[dict[str, int]] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


class DeploymentProfileService:
    def select_profile(
        self,
        profiles: list[DeploymentProfile],
        hospital_id: str,
    ) -> DeploymentProfile | None:
        exact_matches = [profile for profile in profiles if profile.hospital_id == hospital_id]
        active_exact_matches = [
            profile
            for profile in exact_matches
            if (profile.profile_status or "").lower() == "active"
        ]
        if active_exact_matches:
            return active_exact_matches[0]
        if exact_matches:
            return exact_matches[0]

        active_profiles = [
            profile for profile in profiles if (profile.profile_status or "").lower() == "active"
        ]
        if active_profiles:
            return active_profiles[0]
        return profiles[0] if profiles else None

    def seasonality_flags(
        self,
        profile: DeploymentProfile | None,
        as_of: date,
    ) -> dict[str, bool]:
        if profile is None:
            return {
                "seasonality.prealert_active": False,
                "seasonality.high_alert_active": False,
            }

        month = as_of.month
        pre_alert_start = self._month_number(profile.pre_alert_start_month)
        high_alert_start = self._month_number(profile.high_alert_start_month)
        high_alert_end = self._month_number(profile.high_alert_end_month)

        high_alert_active = False
        if high_alert_start is not None and high_alert_end is not None:
            high_alert_active = self._month_in_range(month, high_alert_start, high_alert_end)

        pre_alert_active = False
        if pre_alert_start is not None:
            if high_alert_start is not None:
                pre_alert_active = self._month_in_range(
                    month,
                    pre_alert_start,
                    self._previous_month(high_alert_start),
                )
            else:
                pre_alert_active = month == pre_alert_start

        return {
            "seasonality.prealert_active": pre_alert_active,
            "seasonality.high_alert_active": high_alert_active,
        }

    def _month_number(self, value: str | None) -> int | None:
        if value is None:
            return None
        return MONTH_ORDER.get(value.strip().lower())

    def _month_in_range(self, month: int, start: int, end: int) -> bool:
        if start <= end:
            return start <= month <= end
        return month >= start or month <= end

    def _previous_month(self, month: int) -> int:
        return 12 if month == 1 else month - 1
