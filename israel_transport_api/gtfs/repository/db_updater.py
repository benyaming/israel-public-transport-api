from psycopg import AsyncConnection


async def update_stops(stops: list[list], session: AsyncConnection):

    from psycopg.types import TypeInfo
    from psycopg.types.shapely import register_shapely

    info = await TypeInfo.fetch(session, "geography")
    register_shapely(info, session)

    async with session.cursor() as acur:
        await acur.execute(
            'CREATE TEMP TABLE tmp_stop (LIKE stop INCLUDING DEFAULTS) ON COMMIT DROP'
        )

        insert_query = '''
        COPY tmp_stop (
            id, code, name, street, city, platform, floor, location, 
            location_type, parent_station_id, zone_id
        ) FROM STDIN'''

        async with acur.copy(insert_query) as acopy:
            for stop in stops:
                await acopy.write_row(stop)

        update_query = '''
        INSERT INTO stop 
        SELECT * FROM tmp_stop 
        ON CONFLICT (id) DO UPDATE
        SET 
            id = EXCLUDED.id,
            city = EXCLUDED.city,
            floor = EXCLUDED.floor,
            location = EXCLUDED.location,
            location_type = EXCLUDED.location_type,
            name = EXCLUDED.name,
            parent_station_id = EXCLUDED.parent_station_id,
            platform = EXCLUDED.platform,
            street = EXCLUDED.street,
            zone_id = EXCLUDED.zone_id
        '''
        await acur.execute(update_query)

    await session.commit()


# async def update_db(data: ..., session: AsyncConnection):

