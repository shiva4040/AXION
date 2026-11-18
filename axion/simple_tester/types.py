from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

class ValidationVerdict(str, Enum):
    """
    Structured outcome of mathematical and physical validation.
    """
    VALID = "VALID"                                 # Mathematically, dimensionally, and physically consistent
    INVALID = "INVALID"                             # Mathematical contradiction, dimensional mismatch, or violated constraint
    INCONCLUSIVE = "INCONCLUSIVE"                   # Unable to determine conclusively (e.g. non-linear unsolvable reduction)
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION" # Missing variable definitions, units, or values

class SIDimension(BaseModel):
    """
    Represents physical dimensions as integer exponents of the 7 SI base units:
    [M]^mass * [L]^length * [T]^time * [I]^current * [Θ]^temperature * [N]^amount * [J]^luminosity
    """
    mass: int = 0         # [M] kilogram (kg)
    length: int = 0       # [L] meter (m)
    time: int = 0         # [T] second (s)
    current: int = 0      # [I] ampere (A)
    temperature: int = 0  # [Θ] kelvin (K)
    amount: int = 0       # [N] mole (mol)
    luminosity: int = 0   # [J] candela (cd)

    def is_dimensionless(self) -> bool:
        return all(
            exp == 0
            for exp in [
                self.mass, self.length, self.time, self.current,
                self.temperature, self.amount, self.luminosity
            ]
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SIDimension):
            return False
        return (
            self.mass == other.mass
            and self.length == other.length
            and self.time == other.time
            and self.current == other.current
            and self.temperature == other.temperature
            and self.amount == other.amount
            and self.luminosity == other.luminosity
        )

    def multiply(self, other: "SIDimension") -> "SIDimension":
        return SIDimension(
            mass=self.mass + other.mass,
            length=self.length + other.length,
            time=self.time + other.time,
            current=self.current + other.current,
            temperature=self.temperature + other.temperature,
            amount=self.amount + other.amount,
            luminosity=self.luminosity + other.luminosity,
        )

    def divide(self, other: "SIDimension") -> "SIDimension":
        return SIDimension(
            mass=self.mass - other.mass,
            length=self.length - other.length,
            time=self.time - other.time,
            current=self.current - other.current,
            temperature=self.temperature - other.temperature,
            amount=self.amount - other.amount,
            luminosity=self.luminosity - other.luminosity,
        )

    def power(self, exponent: int) -> "SIDimension":
        return SIDimension(
            mass=self.mass * exponent,
            length=self.length * exponent,
            time=self.time * exponent,
            current=self.current * exponent,
            temperature=self.temperature * exponent,
            amount=self.amount * exponent,
            luminosity=self.luminosity * exponent,
        )

    def to_formula_string(self) -> str:
        if self.is_dimensionless():
            return "[1] (Dimensionless)"
        parts = []
        labels = [
            ("M", self.mass),
            ("L", self.length),
            ("T", self.time),
            ("I", self.current),
            ("Θ", self.temperature),
            ("N", self.amount),
            ("J", self.luminosity),
        ]
        for sym, exp in labels:
            if exp == 1:
                parts.append(f"[{sym}]")
            elif exp != 0:
                parts.append(f"[{sym}]^{exp}")
        return " ".join(parts)

# Pre-defined Common Scientific Dimensions
SI_DIMENSIONLESS = SIDimension()
SI_MASS = SIDimension(mass=1)
SI_LENGTH = SIDimension(length=1)
SI_TIME = SIDimension(time=1)
SI_CURRENT = SIDimension(current=1)
SI_TEMPERATURE = SIDimension(temperature=1)
SI_AMOUNT = SIDimension(amount=1)

SI_AREA = SIDimension(length=2)
SI_VOLUME = SIDimension(length=3)
SI_VELOCITY = SIDimension(length=1, time=-1)
SI_ACCELERATION = SIDimension(length=1, time=-2)
SI_FORCE = SIDimension(mass=1, length=1, time=-2)          # Newton [M][L][T]^-2
SI_ENERGY = SIDimension(mass=1, length=2, time=-2)         # Joule [M][L]^2[T]^-2
SI_POWER = SIDimension(mass=1, length=2, time=-3)          # Watt [M][L]^2[T]^-3
SI_PRESSURE = SIDimension(mass=1, length=-1, time=-2)      # Pascal [M][L]^-1[T]^-2
SI_CHARGE = SIDimension(current=1, time=1)                 # Coulomb [I][T]
SI_VOLTAGE = SIDimension(mass=1, length=2, time=-3, current=-1) # Volt [M][L]^2[T]^-3[I]^-1
SI_RESISTANCE = SIDimension(mass=1, length=2, time=-3, current=-2) # Ohm [M][L]^2[T]^-3[I]^-2
SI_CAPACITANCE = SIDimension(mass=-1, length=-2, time=4, current=2) # Farad

COMMON_DIMENSIONS_CATALOG: Dict[str, SIDimension] = {
    "dimensionless": SI_DIMENSIONLESS,
    "m": SI_LENGTH, "length": SI_LENGTH, "distance": SI_LENGTH, "radius": SI_LENGTH, "x": SI_LENGTH,
    "kg": SI_MASS, "mass": SI_MASS, "m_payload": SI_MASS,
    "s": SI_TIME, "time": SI_TIME, "t": SI_TIME,
    "v": SI_VELOCITY, "velocity": SI_VELOCITY, "speed": SI_VELOCITY,
    "a": SI_ACCELERATION, "acceleration": SI_ACCELERATION, "g": SI_ACCELERATION,
    "f": SI_FORCE, "force": SI_FORCE, "f_drag": SI_FORCE, "f_roll": SI_FORCE,
    "e": SI_ENERGY, "energy": SI_ENERGY, "work": SI_ENERGY, "heat": SI_ENERGY,
    "p": SI_POWER, "power": SI_POWER, "p_solar": SI_POWER, "p_demand": SI_POWER, "p_req": SI_POWER,
    "voltage": SI_VOLTAGE, "v_oc": SI_VOLTAGE,
    "current": SI_CURRENT, "i": SI_CURRENT,
    "r": SI_RESISTANCE, "resistance": SI_RESISTANCE,
    "t_kelvin": SI_TEMPERATURE, "temperature": SI_TEMPERATURE,
    "area": SI_AREA,
    "efficiency": SI_DIMENSIONLESS, "eta": SI_DIMENSIONLESS, "eta_pv": SI_DIMENSIONLESS,
    "c_d": SI_DIMENSIONLESS, "c_rr": SI_DIMENSIONLESS,
}

class PhysicalConstraint(BaseModel):
    """Configurable physical boundary constraint on a parameter."""
    variable_symbol: str
    description: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allow_equal_min: bool = True
    allow_equal_max: bool = True

class ValidationResult(BaseModel):
    """Complete, structured outcome of Component 4 validation."""
    verdict: ValidationVerdict
    equation_checked: str
    is_symbolically_valid: Optional[bool] = None
    is_dimensionally_valid: Optional[bool] = None
    lhs_dimension: Optional[str] = None
    rhs_dimension: Optional[str] = None
    constraints_evaluated: int = 0
    failed_conditions: List[str] = Field(default_factory=list)
    explanation: str
    epistemic_disclaimer: str = (
        "Notice: Validation confirms symbolic, dimensional, and constraint consistency within the "
        "computational model. It does NOT constitute experimental empirical validation."
    )
