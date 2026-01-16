from app.services.wg_stats import WireGuardStatsService

if __name__ == "__main__":
    service = WireGuardStatsService()
    success = service.get_stats()
    if success:
        print("WireGuard data successfully saved.")
    else:
        print("Failed to save WireGuard data.")
