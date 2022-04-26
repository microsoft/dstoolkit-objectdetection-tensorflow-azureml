from azureml.core import Workspace, Environment, Experiment, ScriptRunConfig
from azureml.core.authentication import ServicePrincipalAuthentication
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", type=str, help="Dataset name")
parser.add_argument("--tenant_id", type=str, help="Tenant ID")
parser.add_argument("--service_principal_id", type=str, help="Service Principal ID")
parser.add_argument("--service_principal_password", type=str, help="Serice Principal Password")
parser.add_argument("--subscription_id", type=str, help="Subscription ID")
parser.add_argument("--resource_group", type=str, help="Resource Group")
parser.add_argument("--workspace_name", type=str, help="Workspace Name")
parser.add_argument("--mode", type=str, help="train/infer")
parser.add_argument("--epochs", type=str, default='5', help="Number of training epochs")
parser.add_argument("--model", type=str, default='yolov5s', help="Number of training epochs")

args = parser.parse_args()

sp = ServicePrincipalAuthentication(tenant_id=args.tenant_id,
                                    service_principal_id=args.service_principal_id,
                                    service_principal_password=args.service_principal_password)
ws = Workspace.get(subscription_id=args.subscription_id,
                   resource_group=args.resource_group,
                   name=args.workspace_name,
                   auth=sp)
time_stamp = datetime.now().strftime('%y%m%d_%H%M%S')
env = Environment.get(workspace=ws, name="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu")
env = env.clone("yolo_env")
datastore = ws.get_default_datastore()
dataset_name = args.dataset
if args.mode == 'train':
    src = ScriptRunConfig(source_directory='models/yolo/',
                          script='train_coordinator.py',
                          compute_target='gpu-cluster',
                          environment=env.from_pip_requirements('myenv', 'yolo_requirements.txt'),
                          arguments=['--dataset', dataset_name,
                                     '--cfg', f'{args.model}.yaml',
                                     '--batch-size', '16',
                                     '--epochs', args.epochs])
    print('Starting run')
    run = Experiment(workspace=ws, name='tfod_train').submit(config=src)
    run.wait_for_completion(show_output=True)
    run.download_files('outputs')
    datastore.upload(src_dir='outputs/', target_path=f'yolov5_models/{time_stamp}/', overwrite=False)
elif args.mode == 'infer':
    src = ScriptRunConfig(source_directory='models/yolo/',
                          script='infer_coordinator.py',
                          compute_target='gpu-cluster',
                          environment=env.from_pip_requirements('myenv', 'yolo_requirements.txt'),
                          arguments=['--images', f'{args.dataset}/images/',
                                     '--weights', 'loaded_weights/weights/best.pt',
                                     '--conf', '0.5'])
    print('Starting run')
    run = Experiment(workspace=ws, name='tfod_infer').submit(config=src)
    run.wait_for_completion(show_output=True)
    run.download_files('outputs')
    datastore.upload(src_dir='outputs/', target_path=f'yolov5_inferences/{time_stamp}/', overwrite=False)
elif args.mode == 'test':
    src = ScriptRunConfig(source_directory='models/yolo/',
                          script='test_coordinator.py',
                          compute_target='gpu-cluster',
                          environment=env.from_pip_requirements('myenv', 'yolo_requirements.txt'),
                          arguments=['--dataset', dataset_name,
                                     '--weights', 'loaded_weights/weights/best.pt',
                                     '--conf', '0.5',
                                     '--iou', '0.5'])
    print('Starting run')
    run = Experiment(workspace=ws, name='tfod_test').submit(config=src)
    run.wait_for_completion(show_output=True)
    run.download_files('outputs')
    datastore.upload(src_dir='outputs/', target_path=f'yolov5_tests/{time_stamp}/', overwrite=False)
else:
    print('Invalid argument for mode. Please choose from [\'train\', \'infer\']')
