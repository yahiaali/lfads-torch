import logging

import hydra
import ray
from hydra.utils import instantiate
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)


@hydra.main(config_path="config_run/", config_name="multi_run.yaml")
def main(config: DictConfig):
    print(OmegaConf.to_yaml(config))
    from lfads_torch.run_model import run_model

    # Instantiate the scheduler
    scheduler = instantiate(config.scheduler, _convert_="all")
    # Instantiate the config search space
    search_space = instantiate(config.search_space, _convert_="all")
    # Specify the train config to use
    search_space["config_train"] = config.config_train
    # Clear the GlobalHydra instance so we can compose again in `train`
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    # Run the search with `ray.tune`
    ray_tune_run_params = instantiate(config["ray_tune_run"])
    # ray.init(local_mode=True)
    analysis = ray.tune.run(
        run_model,
        config=search_space,
        scheduler=scheduler,
        **ray_tune_run_params,
    )
    print(f"Best hyperparameters: {analysis.best_config}")


if __name__ == "__main__":
    main()
