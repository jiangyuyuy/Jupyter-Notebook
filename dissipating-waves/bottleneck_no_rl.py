from flow.core.params import SumoParams, EnvParams, NetParams, InitialConfig
from flow.core.params import InFlows, SumoLaneChangeParams, SumoCarFollowingParams
from flow.core.params import VehicleParams
from flow.core.params import TrafficLightParams
from flow.controllers import SimLaneChangeController, ContinuousRouter
from flow.envs import BottleneckEnv
from flow.networks import BottleneckNetwork

import numpy as np
import argparse
import sys
import json
import os
from flow.core.experiment import Experiment
from flow.core.params import AimsunParams
from flow.utils.rllib import FlowParamsEncoder


def dissipating_waves(render, FLOW_RATE):
    
    SCALING = 1
    DISABLE_TB = True

    # If set to False, ALINEA will control the ramp meter
    DISABLE_RAMP_METER = True
    HORIZON = 500

    vehicles = VehicleParams()
    vehicles.add(
        veh_id="human",
        lane_change_controller=(SimLaneChangeController, {}),
        routing_controller=(ContinuousRouter, {}),
        car_following_params=SumoCarFollowingParams(
            speed_mode=25,
        ),
        lane_change_params=SumoLaneChangeParams(
            lane_change_mode=1621),
        num_vehicles=1)

    inflow = InFlows()
    inflow.add(
        veh_type="human",
        edge="1",
        # vehsPerHour=INFLOW,
        vehs_per_hour=FLOW_RATE,
        # departLane="random",
        depart_lane="random",
        # departSpeed=10,
        depart_speed=10)

    traffic_lights = TrafficLightParams()
    if not DISABLE_TB:
        traffic_lights.add(node_id="2")
    if not DISABLE_RAMP_METER:
        traffic_lights.add(node_id="3")


    flow_params = dict(
        # name of the experiment
        exp_tag='bay_bridge_toll',

        # name of the flow environment the experiment is running on
        env_name=BottleneckEnv,

        # name of the network class the experiment is running on
        network=BottleneckNetwork,

        # simulator that is used by the experiment
        simulator='traci',

        # sumo-related parameters (see flow.core.params.SumoParams)
        sim=SumoParams(
            sim_step=0.5,
            render=render,
            overtake_right=False,
            restart_instance=True,
        ),

        # environment related parameters (see flow.core.params.EnvParams)
        env=EnvParams(
            horizon=HORIZON,
            additional_params={
                "target_velocity": 40,
                "max_accel": 1,
                "max_decel": 1,
                "lane_change_duration": 5,
                "add_rl_if_exit": False,
                "disable_tb": DISABLE_TB,
                "disable_ramp_metering": DISABLE_RAMP_METER
            }
        ),

        # network-related parameters (see flow.core.params.NetParams and the
        # network's documentation or ADDITIONAL_NET_PARAMS component)
        net=NetParams(
            inflows=inflow,
            additional_params={
                "scaling": SCALING,
                "speed_limit": 23
            }
        ),

        # vehicles to be placed in the network at the start of a rollout (see
        # flow.core.params.VehicleParams)
        veh=vehicles,

        # parameters specifying the positioning of vehicles upon initialization/
        # reset (see flow.core.params.InitialConfig)
        initial=InitialConfig(
            spacing="random",
            min_gap=5,
            lanes_distribution=float("inf"),
            edges_distribution=["2", "3", "4", "5"]
        ),

        # traffic lights to be introduced to specific nodes (see
        # flow.core.params.TrafficLightParams)
        tls=traffic_lights,
    )

    return Experiment(flow_params)

if __name__=="__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    num_runs = 5
    mean_inflows = []
    mean_outflows = []
    max_outflows = []
    min_outflows = []
    for FLOW_RATE in np.arange(400, 3000, 100):
        exp = dissipating_waves(render=True, FLOW_RATE=FLOW_RATE)
        info_dict = exp.run(num_runs)
        mean_inflow = np.mean(info_dict["inflows"])
        mean_outflow = np.mean(info_dict["outflows"])
        max_outflow = np.max(info_dict["outflows"])
        min_outflow = np.min(info_dict["outflows"])
        mean_inflows.append(mean_inflow)
        mean_outflows.append(mean_outflow)
        max_outflows.append(max_outflow)
        min_outflows.append(min_outflow)
    #plt.figure(figsize=(12, 8))
    plt.plot(mean_inflows, mean_outflows, linewidth=1, c='b', label="inflows-outflows")
    plt.xlabel("inflows/hour")
    plt.ylabel("outflow/hour")
    plt.fill_between(mean_inflows, min_outflows, max_outflows, alpha=0.25, color='b')
    #plt.savefig("bottle.pdf", bbox_inches="tight")
    plt.legend()
    plt.show()
    
    with open("result.txt", "w") as f:
        f.write(str(mean_inflows))
        f.write("\n")
        f.write(str(mean_outflows))
        f.write("\n")
        f.write(str(max_outflows))
        f.write("\n")
        f.write(str(min_outflows))
