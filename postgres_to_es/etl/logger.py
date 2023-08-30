import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(asctime)s - %(message)s'
)

logger = logging.getLogger(__name__)