"""Reusable filtration behavior for mixtures, filtrate, and residue."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FiltrationResult:
    filtered_ml: float
    residue_label: str = "Residue"
    complete: bool = False


class FiltrationEngine:
    def insert_filter_paper(self, funnel):
        funnel.state.transition("filter_paper_inserted")
        return True

    def wet_filter_paper(self, funnel):
        funnel.state.add_flag("wet")
        return True

    def filter(self, source, funnel, receiver, dt: float) -> FiltrationResult:
        if not funnel.state.has("filter_paper_inserted"):
            return FiltrationResult(0.0, complete=False)
        flow_ml = min(source.mixture.volume_ml, max(0.2, 4.0 * dt))
        portion = source.mixture.remove(flow_ml)
        for chemical in portion.contents:
            receiver.mixture.add(chemical)
        funnel.state.transition("filtering")
        receiver.state.transition("receiving_liquid")
        complete = source.mixture.is_empty()
        if complete:
            funnel.state.transition("completed")
        return FiltrationResult(portion.volume_ml, complete=complete)
