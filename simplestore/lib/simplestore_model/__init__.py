import linguistics_metadata_config as LMC
import ecology_metadata_config as EMC
from model import create_metadata_class

metadata_classes = {}
metadata_classes[LMC.domain] = create_metadata_class(LMC)
metadata_classes[EMC.domain] = create_metadata_class(EMC)
