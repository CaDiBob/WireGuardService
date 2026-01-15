from app.services.wg_stats import WireGuardDataService

if __name__ == "__main__":
    service = WireGuardDataService()
    success = service.save()
    if success:
        print("WireGuard data successfully saved.")
    else:
        print("Failed to save WireGuard data.")
