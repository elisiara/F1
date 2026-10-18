"""Modelos e contratos de dados tipados para a OpenF1 API."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Meeting:
    """Representa um evento ou fim de semana de Grande Prêmio."""

    meeting_key: int
    meeting_name: str
    meeting_official_name: str | None
    year: int
    location: str
    country_name: str
    country_code: str | None
    circuit_key: int | None
    circuit_short_name: str
    date_start: str | None
    date_end: str | None
    gmt_offset: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Meeting":
        """Instancia um Meeting a partir de um dicionário da API."""
        return cls(
            meeting_key=int(data["meeting_key"]),
            meeting_name=str(data.get("meeting_name", "")),
            meeting_official_name=data.get("meeting_official_name"),
            year=int(data["year"]),
            location=str(data.get("location", "")),
            country_name=str(data.get("country_name", "")),
            country_code=data.get("country_code"),
            circuit_key=int(data["circuit_key"])
            if data.get("circuit_key") is not None
            else None,
            circuit_short_name=str(data.get("circuit_short_name", "")),
            date_start=data.get("date_start"),
            date_end=data.get("date_end"),
            gmt_offset=data.get("gmt_offset"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para dicionário."""
        return asdict(self)


@dataclass(frozen=True)
class Session:
    """Representa uma atividade oficial de pista (Treino, Quali, Sprint ou Corrida)."""

    session_key: int
    meeting_key: int
    session_name: str
    session_type: str
    year: int
    date_start: str | None
    date_end: str | None
    gmt_offset: str | None
    location: str | None
    circuit_key: int | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        """Instancia uma Session a partir de um dicionário da API."""
        return cls(
            session_key=int(data["session_key"]),
            meeting_key=int(data["meeting_key"]),
            session_name=str(data.get("session_name", "")),
            session_type=str(data.get("session_type", "")),
            year=int(data.get("year", 0)),
            date_start=data.get("date_start"),
            date_end=data.get("date_end"),
            gmt_offset=data.get("gmt_offset"),
            location=data.get("location"),
            circuit_key=int(data["circuit_key"])
            if data.get("circuit_key") is not None
            else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para dicionário."""
        return asdict(self)


@dataclass(frozen=True)
class Driver:
    """Cadastro de piloto participante na sessão."""

    driver_number: int
    session_key: int
    meeting_key: int | None
    full_name: str
    name_acronym: str
    team_name: str | None
    team_colour: str | None
    first_name: str | None
    last_name: str | None
    broadcast_name: str | None
    headshot_url: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Driver":
        """Instancia um Driver a partir de um dicionário da API."""
        return cls(
            driver_number=int(data["driver_number"]),
            session_key=int(data["session_key"]),
            meeting_key=int(data["meeting_key"])
            if data.get("meeting_key") is not None
            else None,
            full_name=str(data.get("full_name", "")),
            name_acronym=str(data.get("name_acronym", "")),
            team_name=data.get("team_name"),
            team_colour=data.get("team_colour"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            broadcast_name=data.get("broadcast_name"),
            headshot_url=data.get("headshot_url"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para dicionário."""
        return asdict(self)


@dataclass(frozen=True)
class Lap:
    """Cronometragem e dados analíticos volta a volta."""

    session_key: int
    meeting_key: int | None
    driver_number: int
    lap_number: int
    lap_duration: float | None
    duration_sector_1: float | None
    duration_sector_2: float | None
    duration_sector_3: float | None
    i1_speed: float | None
    i2_speed: float | None
    st_speed: float | None
    is_pit_out_lap: bool
    date_start: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Lap":
        """Instancia uma Lap a partir de um dicionário da API."""
        lap_dur = data.get("lap_duration")
        s1 = data.get("duration_sector_1")
        s2 = data.get("duration_sector_2")
        s3 = data.get("duration_sector_3")
        i1 = data.get("i1_speed")
        i2 = data.get("i2_speed")
        st = data.get("st_speed")

        return cls(
            session_key=int(data["session_key"]),
            meeting_key=int(data["meeting_key"])
            if data.get("meeting_key") is not None
            else None,
            driver_number=int(data["driver_number"]),
            lap_number=int(data.get("lap_number", 0)),
            lap_duration=float(lap_dur) if lap_dur is not None else None,
            duration_sector_1=float(s1) if s1 is not None else None,
            duration_sector_2=float(s2) if s2 is not None else None,
            duration_sector_3=float(s3) if s3 is not None else None,
            i1_speed=float(i1) if i1 is not None else None,
            i2_speed=float(i2) if i2 is not None else None,
            st_speed=float(st) if st is not None else None,
            is_pit_out_lap=bool(data.get("is_pit_out_lap", False)),
            date_start=data.get("date_start"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para dicionário."""
        return asdict(self)


@dataclass(frozen=True)
class TelemetrySample:
    """Amostra de telemetria de alta frequência (~3.7 Hz) de um carro."""

    date: str
    driver_number: int
    session_key: int
    meeting_key: int | None
    speed: float
    rpm: int
    n_gear: int
    throttle: float
    brake: float
    drs: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TelemetrySample":
        """Instancia uma TelemetrySample a partir de um dicionário da API."""
        return cls(
            date=str(data.get("date", "")),
            driver_number=int(data["driver_number"]),
            session_key=int(data["session_key"]),
            meeting_key=int(data["meeting_key"])
            if data.get("meeting_key") is not None
            else None,
            speed=float(data.get("speed", 0.0)),
            rpm=int(data.get("rpm", 0)),
            n_gear=int(data.get("n_gear", 0)),
            throttle=float(data.get("throttle", 0.0)),
            brake=float(data.get("brake", 0.0)),
            drs=int(data.get("drs", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para dicionário."""
        return asdict(self)


@dataclass(frozen=True)
class WeatherSample:
    """Condições meteorológicas capturadas no circuito."""

    date: str
    session_key: int
    meeting_key: int | None
    air_temperature: float | None
    track_temperature: float | None
    humidity: float | None
    pressure: float | None
    rainfall: int
    wind_speed: float | None
    wind_direction: int | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WeatherSample":
        """Instancia um WeatherSample a partir de um dicionário da API."""
        air = data.get("air_temperature")
        track = data.get("track_temperature")
        hum = data.get("humidity")
        press = data.get("pressure")
        wind = data.get("wind_speed")
        wind_dir = data.get("wind_direction")

        return cls(
            date=str(data.get("date", "")),
            session_key=int(data["session_key"]),
            meeting_key=int(data["meeting_key"])
            if data.get("meeting_key") is not None
            else None,
            air_temperature=float(air) if air is not None else None,
            track_temperature=float(track) if track is not None else None,
            humidity=float(hum) if hum is not None else None,
            pressure=float(press) if press is not None else None,
            rainfall=int(data.get("rainfall", 0)),
            wind_speed=float(wind) if wind is not None else None,
            wind_direction=int(wind_dir) if wind_dir is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para dicionário."""
        return asdict(self)


@dataclass(frozen=True)
class SessionResult:
    """Resultado final homologado após conclusão da sessão."""

    position: int | None
    driver_number: int
    session_key: int
    meeting_key: int | None
    number_of_laps: int | None
    duration: float | None
    gap_to_leader: str | None
    dnf: bool
    dns: bool
    dsq: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionResult":
        """Instancia um SessionResult a partir de um dicionário da API."""
        pos = data.get("position")
        laps = data.get("number_of_laps")
        dur = data.get("duration")

        return cls(
            position=int(pos) if pos is not None else None,
            driver_number=int(data["driver_number"]),
            session_key=int(data["session_key"]),
            meeting_key=int(data["meeting_key"])
            if data.get("meeting_key") is not None
            else None,
            number_of_laps=int(laps) if laps is not None else None,
            duration=float(dur) if dur is not None else None,
            gap_to_leader=str(data["gap_to_leader"])
            if data.get("gap_to_leader") is not None
            else None,
            dnf=bool(data.get("dnf", False)),
            dns=bool(data.get("dns", False)),
            dsq=bool(data.get("dsq", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para dicionário."""
        return asdict(self)
