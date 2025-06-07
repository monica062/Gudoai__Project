# gudoai_cli.py
import argparse
from gudoai_core import GudoaiCore

def main():
    parser = argparse.ArgumentParser(description="GUDOAI - Grand Unified DevOps Orchestrator & API Interrogator")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # gudoai init <project_name>
    init_parser = subparsers.add_parser('init', help='Initialize a new micro-project')
    init_parser.add_argument('project_name', type=str, help='Name of the project to initialize')

    # gudoai update_meta <project_name> --description "<new_description>"
    update_parser = subparsers.add_parser('update_meta', help='Update project description')
    update_parser.add_argument('project_name', type=str, help='Name of the project')
    update_parser.add_argument('--description', type=str, required=True, help='New description for the project')

    # gudoai create_feature_branch <project_name> <branch_name>
    branch_parser = subparsers.add_parser('create_feature_branch', help='Create a feature branch')
    branch_parser.add_argument('project_name', type=str, help='Name of the project')
    branch_parser.add_argument('branch_name', type=str, help='Name of the feature branch')

    # gudoai merge_to_main <project_name> <feature_branch_name>
    merge_parser = subparsers.add_parser('merge_to_main', help='Merge feature branch into main')
    merge_parser.add_argument('project_name', type=str, help='Name of the project')
    merge_parser.add_argument('feature_branch_name', type=str, help='Name of the feature branch to merge')

    # Subparser untuk register_project
    reg_parser = subparsers.add_parser('register_project', help='Register project with external API')
    reg_parser.add_argument('project_name', type=str, help='Name of the project')

    # Subparser untuk sync_project
    sync_parser = subparsers.add_parser('sync_project', help='Sync project state with API')
    sync_parser.add_argument('project_name', type=str, help='Name of the project')

    # Subparser untuk check_api_status
    status_parser = subparsers.add_parser('check_api_status', help='Check project status from API')
    status_parser.add_argument('project_name', type=str, help='Name of the project')

    args = parser.parse_args()

    core = GudoaiCore()

    try:
        if args.command == 'init':
            core.init_project(args.project_name)
        elif args.command == 'update_meta':
            core.update_metadata(args.project_name, args.description)
        elif args.command == 'create_feature_branch':
            core.create_feature_branch(args.project_name, args.branch_name)
        elif args.command == 'merge_to_main':
            if not core.merge_to_main(args.project_name, args.feature_branch_name):
                print("[ERROR] Merge failed due to conflicts.")
        elif args.command == 'register_project':
            core.register_project(args.project_name)
        elif args.command == 'sync_project':
            core.sync_project(args.project_name)
        elif args.command == 'check_api_status':
            core.check_api_status(args.project_name)
        else:
            parser.print_help()
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    main()