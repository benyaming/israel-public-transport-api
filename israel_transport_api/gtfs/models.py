from enum import StrEnum

from pydantic import BaseModel, computed_field


class StopTypeConstants:
    jerusalem_light_rail = 'מסילת ברזל'
    gush_dan_light_rail = 'מסילת ברזל קו אדום גוש דן'
    railway_station = 'תחנת רכבת'


class StopType(StrEnum):
    bus_stop = 'bus_stop'
    bus_central_station = 'bus_central_station'
    bus_central_station_platform = 'bus_central_station_platform'
    jerusalem_light_rail_stop = 'jerusalem_light_rail_stop'
    gush_dan_light_rail_station = 'gush_dan_light_rail_station'
    gush_dan_light_rail_platform = 'gush_dan_light_rail_platform'
    railway_station = 'railway_station'


class Agency(BaseModel):
    id: int
    name: str
    url: str
    phone: str


class Route(BaseModel):
    id: int
    agency: Agency
    short_name: str
    from_stop_name: str
    to_stop_name: str
    from_city: str
    to_city: str
    description: str
    type: int
    color: str

    @classmethod
    def from_row(cls, row: list) -> 'Route':
        return cls(
            id=row[0],
            short_name=row[2],
            from_stop_name=row[3],
            to_stop_name=row[4],
            from_city=row[5],
            to_city=row[6],
            description=row[7],
            type=row[8],
            color=row[9],
            agency=Agency(
                id=row[10],
                name=row[11],
                url=row[12],
                phone=row[15]
            )
        )


class StopLocation(BaseModel):
    type: str = 'Point'
    coordinates: tuple[float, float]


class Stop(BaseModel):
    id: int
    code: int
    name: str
    city: str | None = None
    street: str | None = None
    floor: int | None = None
    platform: int | None = None
    location: StopLocation
    location_type: int
    parent_station_id: int | None = None
    zone_id: int | None = None
    
    @computed_field
    @property
    def stop_type(self) -> StopType:
        if self.location_type == 1:
            if self.street == StopTypeConstants.gush_dan_light_rail:
                return StopType.gush_dan_light_rail_station
            return StopType.bus_central_station
        elif self.street == StopTypeConstants.jerusalem_light_rail:
            return StopType.jerusalem_light_rail_stop
        elif self.street == StopTypeConstants.gush_dan_light_rail and self.platform is not None:
            return StopType.gush_dan_light_rail_platform
        elif self.floor == StopTypeConstants.railway_station or self.city is None:
            return StopType.railway_station
        elif self.platform is not None:
            return StopType.bus_central_station_platform
        
        return StopType.bus_stop

    @classmethod
    def from_row(cls, row: list) -> 'Stop':
        return cls(
            id=row[0],
            code=row[2],
            name=row[6],
            city=row[1],
            street=row[9],
            floor=row[3],
            platform=row[8],
            location=StopLocation(coordinates=(row[11], row[12])),
            location_type=row[5],
            parent_station_id=row[7],
            zone_id=row[10]
        )

    class Config:
        collection = 'stops'

        json_schema_extra = {
            'example': {
                'id': 10846,
                'code': 5200,
                'name': 'בנייני האומה',
                'city': 'ירושלים',
                'street': 'שדרות שז''ר',
                'floor': None,
                'platform': None,
                'location': {
                    'type': 'Point',
                    'coordinates': [31.787909, 35.203428]
                },
                'location_type': '0',
                'parent_station_id': '',
                'zone_id': '3000'
            }
        }
