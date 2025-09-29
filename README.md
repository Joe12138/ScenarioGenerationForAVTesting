# ScenarioGenerationForAVTesting

Generate driving scenarios from scratch for ADS.

## Environment Setup
> Note: This codebase has been tested primarily on Ubuntu 20.04 with Python 3.9

- Create a virtual environment with `conda create -n autoscecraft python=3.9` and activated it `conda activate autoscecraft`.
- Update pip with `pip install --upgrade pip`
- Install remaining dependencies, including `pyclothoids, numpy, copy`

## Driving Scenario Generation
To generate static driving scenarios, follow these steps:

1. **Run the Road Network Generator**

    Execute the following command to generate a static driving scenario based on your specifications:

    `python road_network_generator.py`

2. **Customization Options**
    
    You can customize the generated scenarios by modifying the configuration parameters in the script. These parameters control aspects such as road types, intersections, lane configurations, and more. Refer to the script comments and documentation to adjust these settings according to your requirements.

3. **Output Files**

    The script will generate the scenario files, which include detailed descriptions of the road network, traffic rules, and any static obstacles or elements. These files are essential for creating realistic and reproducible driving environments.

4. **Example Scenario**
    
    After running the generator, you should see output similar to:

    ```Scenario generated successfully at: /path/to/scenario/```

    The folder will contain various files like road network models, lane configurations, and additional metadata for simulation purposes.

## Integrating with Popular Simulators
### Integrating with SMARTS

1. **Install SMARTS Simulator**
    
    First, you need to install the SMARTS simulator. SMARTS is an open-source, multi-agent reinforcement learning platform for autonomous driving research. To install SMARTS, follow the instructions in the official SMARTS GitHub repository.

    ```
    git clone https://github.com/huawei-noah/SMARTS.git
    cd SMARTS
    pip install -r requirements.txt
    pip install -e .
    ```

2. **Move the Generated Scenario Files**
    
    After running the road network generator, take the generated static driving scenario files (e.g., road network, object definitions, etc.) and move them to the scenarios/open_drive folder inside the SMARTS project directory. You can do this manually or via a script:

    `mv /path/to/generated_scenario/* /path/to/SMARTS/scenarios/open_drive/`
    
    Make sure the file structure inside the open_drive folder matches the expectations of the SMARTS simulator.

3. **Create and Customize scenario.py**
    Next, you need to create a Python script, scenario.py, that defines how the generated driving scenarios will be used in the SMARTS simulator. This script will load the scenario files and configure agents (vehicles, pedestrians, etc.) within the environment.

    Here is an example structure for scenario.py:

    ```Python
    from smarts.core.agent import Agent
    from smarts.core.scenario import Scenario

    # Load the scenario (assuming scenario files are in the open_drive folder)
    scenario = Scenario("open_drive/scenario_name")

    # Initialize agents and vehicles
    agent = Agent()
    scenario.add_agent(agent)

    # Setup simulation parameters, including time step, vehicle models, and traffic behavior
    scenario.set_simulation_parameters(time_step=0.1, vehicle_model="default", traffic_behavior="dynamic")

    # Start the simulation
    scenario.run()
    ```

4. **Run the SMARTS Simulation**
    
    After setting up the `scenario.py` script, you can run the SMARTS simulator to visualize and interact with the generated driving scenarios.

### Integrating with CARLA Simulator

To integrate the generated driving scenarios with the CARLA simulator, follow these steps:

1. **Install CARLA Simulator**  
   
   First, you need to install CARLA, an open-source autonomous driving simulator. CARLA provides a realistic environment for testing and evaluating autonomous vehicle systems. To install CARLA, follow the instructions in the official [CARLA GitHub repository](https://github.com/carla-simulator/carla).

2. **Set Up the CARLA Server**
    
    Before running any scenarios, you need to start the CARLA server. Open a terminal and run the following command:

    ```
    ./CarlaUE4.sh  # On Linux
    # Or
    CarlaUE4.exe  # On Windows
    ```

3. **Move the Generated Scenario Files**

    Once you have generated the driving scenario using the road_network_generator.py, you’ll need to convert and move the scenario files to a format compatible with CARLA. CARLA uses OpenDRIVE (.xodr) files for the road network and additional configuration files for the agents and traffic.
    - **Move the OpenDRIVE file to CARLA:** Copy the .xodr file and any other necessary assets (such as traffic configuration, agent models, etc.) to the CARLA/Content/Maps folder.

4. **Create and Customize `spawn_vehicles.py`**

    Next, you need to create a Python script, `spawn_vehicles.py`, to load the generated scenario and spawn vehicles, pedestrians, and other agents within the CARLA environment.

    A basic `spawn_vehicles.py` example:
    ```Python
    import carla
    import random

    def spawn_vehicle(world, blueprint_library):
        vehicle_bp = blueprint_library.filter('vehicle')[0]  # Choose a vehicle blueprint
        spawn_point = random.choice(world.get_map().get_spawn_points())  # Random spawn point
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        vehicle.set_autopilot(True)  # Enable autopilot for autonomous behavior
        return vehicle

    def main():
        # Connect to the CARLA server
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        world = client.get_world()

        # Get the blueprint library and spawn vehicles
        blueprint_library = world.get_blueprint_library()
        vehicle = spawn_vehicle(world, blueprint_library)

        # Run the simulation
        try:
            while True:
                world.tick()  # Advance the simulation
        finally:
            vehicle.destroy()

    if __name__ == "__main__":
        main()
    ```

5. **Run the CARLA Simulation**
    
    Once you have set up the spawn_vehicles.py script, you can run it to load the generated scenario in the CARLA simulator. The CARLA server should already be running.

    `python spawn_vehicles.py`
    
    This will start the simulation, and vehicles will begin to move within the CARLA environment based on the generated road network and traffic configurations.

## Testing the modules of ADS
### Testing Perception module
1. Collect data in CARLA simulator with [CARLA Dataset Tools](https://github.com/KevinLADLee/carla_dataset_tools).
2. Find pre-trained or train your own perception model[GLENet](https://github.com/Eaphan/GLENet).
3. Test the perception models with collected data.

### Testing Prediction module
1. Data collection in SMARTS/CARLA simulator.
2. Find pre-trained or train your own vehicle trajectroy prediction (VTP) models.
    - Several SOTA VTP models: [HiVT](https://github.com/ZikangZhou/HiVT), [QCNet](https://github.com/ZikangZhou/QCNet), [HPNet](https://github.com/XiaolongTang23/HPNet)
3. Test the VTP models with collected data.

### Testing Planning module
1. Integrating this package into SMARTS simulator.
2. Find pre-trained or train your own planning model[PD-planner](https://github.com/MCZhi/Predictive-Decision).
3. Test the planning model in SMARTS simulator.

<!-- ## TODO
- [x] Add the code of road network generator
- [x] Add the code of traffic rule generator
- [x] Add the code of roadside structure generator
- [ ] Add the code of dynamic object generator
- [x] Add the code of experiments -->


Please consider citing this work if you use this repository. The bibtex is as below:
```
@article{Lan2025, 
    author = {Wenxing Lan and Jialin Liu and Bo Yuan and Xin Yao},
    title = {AutoSceCraft: Generate Various Driving Scenarios from Scratch for Autonomous Driving Systems},
    year = {2025},
    journal = {Tsinghua Science and Technology},
    keywords = {autonomous driving, driving simulator, road network generation, driving scenario generation, procedural content generation},
    url = {https://www.sciopen.com/article/10.26599/TST.2025.9010045},
    doi = {10.26599/TST.2025.9010045}
}
```