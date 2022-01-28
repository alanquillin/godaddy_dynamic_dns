import logging
import os
import sys
import time

from dynamic_dns_updater import DynamicDNSUpdater

LOG_FMT = "%(levelname)-8s: %(asctime)-15s [%(name)s]: %(message)s"

if __name__ == "__main__":
    log_level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    if root_logger.handlers:
        for log_handler in root_logger.handlers:
            log_handler.setFormatter(logging.Formatter(fmt=LOG_FMT))
    logging.basicConfig(level=log_level, format=LOG_FMT)

    logger = logging.getLogger(__name__)

    updater = DynamicDNSUpdater(
        base_url=os.environ.get("BASE_URL", "https://api.godaddy.com/v1"),
        sso_key=os.environ.get("SSO_KEY"),
        sso_secret=os.environ.get("SSO_SECRET"),
        domain=os.environ.get("DOMAIN"),
        record=os.environ.get("RECORD"),
        record_type=os.environ.get("RECORD_TYPE", "A"),
        dry_run=os.environ.get("DRY_RUN", "false").lower() == "true"
    )

    try:
        interval = int(os.environ.get("INTERVAL", "300"))
        loop = os.environ.get("LOOP", "true").lower() == "true"

        while True:
            updater.run()
            if not loop:
                break
            time.sleep(interval)
            pass
    except KeyboardInterrupt:
        logger.info("User interrupted - Goodbye")
        sys.exit()
