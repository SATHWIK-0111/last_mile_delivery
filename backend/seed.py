from app.database import Base, SessionLocal, engine
from app.models.user import User
from app.models.zone import Zone
from app.models.zone_area import ZoneArea
from app.models.rate_card import RateCard
from app.models.cod_charge import CodCharge
from app.utils.auth import hash_password


def seed_database():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:

        # -----------------------------
        # ADMIN
        # -----------------------------

        admin = (
            db.query(User)
            .filter(User.email == "admin@lastmile.com")
            .first()
        )

        if not admin:

            admin = User(
                name="System Admin",
                email="admin@lastmile.com",
                phone="9999999999",
                password_hash=hash_password("Admin@123"),
                role="ADMIN"
            )

            db.add(admin)

        # -----------------------------
        # ZONES
        # -----------------------------

        zone_data = [
            "Zone A",
            "Zone B",
            "Zone C",
        ]

        zones = {}

        for zone_name in zone_data:

            zone = (
                db.query(Zone)
                .filter(Zone.name == zone_name)
                .first()
            )

            if not zone:
                zone = Zone(name=zone_name)
                db.add(zone)
                db.flush()

            zones[zone_name] = zone

        # -----------------------------
        # AREAS
        # -----------------------------

        area_data = {
            "Zone A": [
                "Vijayawada",
                "Mangalagiri",
                "Gannavaram",
            ],
            "Zone B": [
                "Guntur",
                "Tenali",
                "Amaravati",
            ],
            "Zone C": [
                "Chennai",
                "Tambaram",
                "Guindy",
            ],
        }

        for zone_name, areas in area_data.items():

            for area_name in areas:

                existing = (
                    db.query(ZoneArea)
                    .filter(
                        ZoneArea.zone_id == zones[zone_name].id,
                        ZoneArea.area_name == area_name
                    )
                    .first()
                )

                if not existing:

                    db.add(
                        ZoneArea(
                            zone_id=zones[zone_name].id,
                            area_name=area_name
                        )
                    )

        # -----------------------------
        # RATE CARDS
        # -----------------------------

        rates = [
            ("B2B", "INTRA", 40, 15),
            ("B2B", "INTER", 60, 20),
            ("B2C", "INTRA", 50, 20),
            ("B2C", "INTER", 75, 25),
        ]

        for order_type, zone_type, base, additional in rates:

            existing = (
                db.query(RateCard)
                .filter(
                    RateCard.order_type == order_type,
                    RateCard.zone_type == zone_type
                )
                .first()
            )

            if not existing:

                db.add(
                    RateCard(
                        order_type=order_type,
                        zone_type=zone_type,
                        base_rate=base,
                        additional_rate=additional,
                        weight_limit=1
                    )
                )

        # -----------------------------
        # COD CHARGES
        # -----------------------------

        cod_data = [
            ("B2B", 30),
            ("B2C", 25),
        ]

        for order_type, charge in cod_data:

            existing = (
                db.query(CodCharge)
                .filter(
                    CodCharge.order_type == order_type
                )
                .first()
            )

            if not existing:

                db.add(
                    CodCharge(
                        order_type=order_type,
                        charge=charge
                    )
                )

        db.commit()

        print("Database seeded successfully!")
        print()
        print("Admin:")
        print("Email: admin@lastmile.com")
        print("Password: Admin@123")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()