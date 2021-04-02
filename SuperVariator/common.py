from dataclasses import dataclass


@dataclass
class CutSpec:
    shower_pe: float
    shower_sec: float
    delayed_emin_mev: float
    prompt_emin_mev: float

    @staticmethod
    def from_str(s):
        "Expects a string of the form 'shower_pe=3e5,shower_sec=1.4...'"
        # s_com = ', '.join(s.split())
        # return eval(f"CutSpec({s_com})")
        return eval(f"CutSpec({s})")
