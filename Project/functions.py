from re import compile
from time import sleep
from getpass import getpass
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
DEBUG = False


# Functions for main
def validate_url(input_url: str):
    """
    :param input_url: three.part.url
    :return: original or updated input_url if validation prompted change
    """
    input_url = input_url.lower()
    if 'http' in input_url:
        input_url = input_url.split('://')[1]
    # Regex: Str().lower() any length + period + Str().lower() any length + com/net/org/io/etc
    pattern = compile(r'[a-z0-9]+\.[a-z0-9]+\.(com|net|org|gov|io|au|ca|de|ie|nz|us|services)')
    matches = pattern.finditer(input_url)
    # Find matches of regex
    match_list = [match for match in matches]

    # List of matches is blank, re-prompt until match
    while not match_list:
        print('Invalid input -- no need for http/https')
        input_url = input('Provide VSA Url: ')
        matches = pattern.finditer(input_url)

        # Find matches of regex
        match_list = [match for match in matches]

    # return original input, or modified input if originally invalid
    return input_url


# # # PACKAGE FUNCTIONS - Import as needed
def print_err():
    print('Unable to match path specified, invalid xpath or null, trying default')


def login(driver):
    """
    :param driver: object for selenium webDriver
    :return: nothing, or fail message.
    """
    sleep(0.5)
    authenticated = False
    # # # Username and password entry # # #
    while not authenticated:
        # User
        user = input('Provide the username: ')
        check = driver.find_elements_by_xpath('//input[@id="UsernameTextbox"]')
        if not check:
            raise ValueError('No accessible XPATH for username. Are you at the login screen?')
        check[0].clear()
        check[0].send_keys(user)

        # Pass
        if DEBUG:
            pw = input('Provide your password (input mask disabled): ')
        else:
            pw = getpass('Provide your password (input mask enabled): ')
        check = driver.find_elements_by_xpath('//input[@id="PasswordTextbox"]')
        if not check:
            raise ValueError('No accessible XPATH for password. Are you at the login screen?')
        check[0].clear()
        check[0].send_keys(pw)

        # Submit
        driver.find_element_by_xpath('//input[@id="SubmitButton"]').click()
        sleep(1)

        # Error check
        error_check = driver.find_elements_by_xpath('//div[@class="loginerror"]')
        if not error_check:
            print('Authentication successful\n')
            authenticated = True
        else:
            print('Authentication failed - Invalid user/pass combo\n')
    sleep(1)

    # # # MFA HANDLING # # #
    timeout = 0
    while timeout <= 3:
        sleep(1)
        timeout += 1
        # MFA Configured? Is there a skip button?
        mfa_xpath = driver.find_elements_by_xpath('//input[contains(@maxlength,"6")]')
        mfa_xpath.append(driver.find_elements_by_xpath(
            '//label[contains(text(),"AuthAnvil") or contains(text(),"Passly")]'))
        if mfa_xpath:
            break

    mfa_xpath = driver.find_elements_by_xpath('//input[contains(@maxlength,"6")]')
    mfa_xpath.append(driver.find_elements_by_xpath(
        '//label[contains(text(),"AuthAnvil") or contains(text(),"Passly")]'))
    if not mfa_xpath:
        sleep(2)
        try:
            driver.find_element_by_xpath(agent(driver)).click()
        except NoSuchElementException:
            print('Unable to locate MFA input. Unable to locate side panel nav.')
            print('Please ensure that MFA is configured for the user before executing this application.')
        else:
            pass
    else:
        try:
            mfa_xpath[0].send_keys('111111')
        except ElementNotVisibleException:
            pass
        else:
            mfa_xpath[0].clear()
            # MFA needs to be entered.
            authenticated = False
            while not authenticated:
                # Standard Kaseya MFA check
                mfa_input = driver.find_elements_by_xpath('//input[contains(@maxlength,"6")]')
                if not mfa_input:
                    # Auth Anvil check
                    check = driver.find_elements_by_xpath(
                        '//label[contains(text(),"AuthAnvil") or contains(text(),"Passly")]')
                    if check:
                        # AuthAnvil confirmed
                        mfa_input = driver.find_elements_by_xpath('//input[@type="password" and @role="textbox"]')
                        mfa_code = input('Provide the MFA OTP (AuthAnvil/Passly): ')
                        submit_button = driver.find_element_by_xpath(
                            '/html/body/div[3]/div/span/div/div/div/span/div/a/span/span/span[2]')
                        mfa_input[0].clear()
                        mfa_input[0].send_keys(mfa_code)
                        submit_button.click()
                        sleep(1)

                        error_check = driver.find_elements_by_xpath('//input[@id="UsernameTextbox"]')
                        if not error_check:
                            print('Authentication successful (AuthAnvil/Passly)\n')
                            authenticated = True
                        else:
                            print('Authentication failed - Invalid MFA code\n')
                    else:
                        # No match, or invalid Auth Anvil entry (returns to un/pw submission - exit)
                        print('Unable to locate MFA input XPATH')
                        print('If you entered an invalid code for AuthAnvil, restart this script.')
                        print('Sleeping for 10s - CTRL+C to exit early.')
                        sleep(10)
                        driver.quit()
                        exit(87)
                        break
                else:
                    # Standard Kaseya MFA confirmed
                    mfa_code = input('Provide the MFA OTP: ')
                    submit_button = driver.find_element_by_xpath('//button[text()="Submit"]')
                    mfa_input[0].clear()
                    mfa_input[0].send_keys(mfa_code)
                    submit_button.click()
                    sleep(1)

                    error_check = driver.find_elements_by_xpath('//div[@class="authCodeError"]')
                    if not error_check:
                        print('Authentication successful\n')
                        authenticated = True
                    else:
                        print('Authentication failed - Invalid MFA code\n')


def logout(driver):
    """
    :param driver: object for selenium webDriver
    :return:
    """
    check = driver.find_elements_by_xpath('//*[@id="BannerBar"]/div/div[1]/div[3]/i/div')
    if not check:
        return 'No accessible xpath. Are you on the main Kaseya page?'

    check[0].click()
    driver.find_element_by_xpath('//*[@id="BannerBar"]/div/div[1]/div[3]/i/div[2]/div/div/div[6]/span').click()


def hamburger(driver):
    xpath = '//*[@id="leftNavTopRow"]'
    check = driver.find_elements_by_xpath(xpath)
    if not check:
        print('Main hamburger not accessible. Are you controlling the correct window?')
        return False
    return driver.find_element_by_xpath(xpath)


def panel_open(driver):
    # create a one-element list if element is found, else null list[]
    check = driver.find_elements_by_xpath('//h3[contains(text(),"Agent Procedures")]')
    if not check:
        hamburger(driver).click()

    check = driver.find_elements_by_xpath('//h3[contains(text(),"Agent Procedures")]')
    if not check:
        print('Error locating hamburger xpath, unable to reach nested element')
        return False
    return True


# Funcs below are clones of one another to access side panel modules
def agent(driver, location=''):
    """
    :param driver: object for selenium webDriver
    :param location: Kaseya UI side panel menu location - use list below for names
    :return:
    """
    default = '//h3[text()="Agent"]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'manage_agents': default,
            'agent_logs': '',
            'log_history': '',
            'event_log_settings': '',
            'screen_recordings': '',
            'manage_packages': '',
            'create': '',
            'rename': '',
            'delete': '',
            'change_group': '',
            'set_credential': '',
            'copy_settings': '',
            'import_export': '',
            'agent_menu': '',
            'edit_profile': '',
            'portal_access': '',
            'lan_cache': '',
            'assign_lan_cache': '',
            'file_access': '',
            'network_access': '',
            'application_blocker': '',
            'application_logging': '',
            'configuration': '',
            'dashboard': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def agent_procedures(driver, location=''):
    default = '//h3[contains(text(),"Agent Procedures")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'schedule_create': '//*[contains(@data-nav-id,"8098")]',
            'distribution': '',
            'agent_procedure_status': '',
            'overview': '',
            'pending_approvals': '',
            'patch_deploy': '',
            'application_deploy': '',
            'get_file': '',
            'distribute_file': '',
            'application_logging': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def anti_malware(driver, location=''):
    default = '//h3[contains(text(),"Anti-Malware")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'machines': default,
            'dashboards': '',
            'detections': '',
            'profiles': '',
            'alerts': '',
            'settings': '',
            'application_logging': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def antivirus(driver, location=''):
    default = '//h3[contains(text(),"Antivirus")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'machines': default,
            'dashboards': '',
            'detections': '',
            'profiles': '',
            'alerts': '',
            'settings': '',
            'application_logging': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def audit(driver, location=''):
    default = '//h3[contains(text(),"Audit")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'view_assets': default,
            'manage_credentials': '',
            'credential_log': '',
            'run_audit': '',
            'audit_summary': '',
            'configure_column_sets': '',
            'machine_summary': '',
            'system_info': '',
            'installed_apps': '',
            'add_remove': '',
            'software_licenses': '',
            'documents': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def backup(driver, location=''):
    default = '//h3[text()="Backup"]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'backup_status': default,
            'schedule_volumes': '',
            'pre_post_procedure': '',
            'schedule_folder': '',
            'backup_sets': '',
            'backup_logs': '',
            # Recovery
            'explore_volumes': '',
            'explore_folders': '',
            'verify_images': '',
            'image_to_vm': '',
            'auto_recovery': '',
            'cd_recovery': '',
            'universal_restore': '',
            # Offsite Replication
            'offsite_servers': '',
            'local_servers': '',
            'offsite_alert': '',
            'schedule_xfer': '',
            # Configure
            'install_remove': '',
            'image_location': '',
            'image_password': '',
            'folder_backup': '',
            'backup_alert': '',
            'compression': '',
            'max_file_size': '',
            'max_log_age': '',
            'secure_zone': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def cloud_backup(driver, location=''):
    default = '//h3[contains(text(),"Cloud Backup")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
            'dashboards': '',
            'machines': '',
            'acronis_alert_hist': '',
            'acronis_backup_hist': '',
            # Configuration
            'profiles': '',
            'alerts': '',
            'backup_groups': '',
            'settings': '',
            # Admin
            'app_logging': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def data_backup(driver, location=''):
    default = '//h3[contains(text(),"Data Backup")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
            # Backup
            'status': '',
            'schedule': '',
            'logs': '',
            # Recovery
            'restore': '',
            'manage': '',
            # Storage
            'summary': '',
            # Configure
            'install_remove': '',
            'backup_profiles': '',
            'alerts': '',
            'private_storage': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def desktop_mgmt(driver, location=''):
    default = '//h3[contains(text(),"Desktop Management")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
            # Wake on LAN
            'schedule': '',
            'alerts': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def discovery(driver, location=''):
    default = '//h3[contains(text(),"Discovery")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def info_center(driver, location=''):
    default = '//h3[contains(text(),"Info Center")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'inbox': default,
            # Networks
            'by_network': '',
            'by_agent': '',
            'devices': '',
            'devices_tile': '',
            # Domains
            'domain_watch': '',
            'computers': '',
            'users_portal_access': '',
            # Admin
            'settings': '',
            'audit_log': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def monitor(driver, location=''):
    default = '//h3[text()="Monitor"]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'dashboard_list': default,
            'dashboard_settings': '',
            # Status
            'alarm_summary': '',
            'suspend_alarm': '',
            'live_counter': '',
            # Edit
            'monitor_lists': '',
            'update_lists_scan': '',
            'monitor_sets': '//*[contains(@data-nav-id,"11010")]',
            'snmp_sets': '',
            'add_snmp_obj': '',
            # Agent Monitoring
            'alerts': '//*[contains(@data-nav-id,"11014")]',
            'event_log_alerts': '//*[contains(@data-nav-id,"11029")]',
            'snmp_traps_alerts': '',
            'assign_monitoring': '//*[contains(@data-nav-id,"11015")]',
            'monitor_log': '',
            # External Monitoring
            'system_check': '',
            # SNMP Monitoring
            'assign_snmp': '',
            'snmp_log': '',
            'set_snmp_val': '',
            'set_snmp_type': '',
            # Log monitoring
            'parser_summary': '',
            'log_parser': '',
            'assign_parser_sets': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def network_monitor(driver, location=''):
    default = '//h3[contains(text(),"Network Monitor")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
            # Monitoring
            'view_monitoring': '',
            # Reports
            'view_reports': '',
            'report_templates': '',
            'report_styles': '',
            # KB
            'view_knowledgebase': '',
            # Dashboard
            'view_dashboard': '',
            # Schedules
            'device_maintenance': '',
            'monitor_maintenance': '',
            'user_notification_sched': '',
            # Tools
            'manage_windows_svc': '',
            'mib_browser': '',
            'record_manager_log': '',
            'syslog_msg': '',
            'system_admin_console': '',
            'system_log': '',
            'trap_msgs': '',
            'utility_downloads': '',
            # User
            'my_settings': '',
            'user_notification': '',
            # Settings
            'custom_datatypes': '',
            'device_templates': '',
            'log_settings': '',
            'noc_config': '',
            'other_sys_settings': '',
            'sms': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def patch_mgmt(driver, location=''):
    default = '//h3[contains(text(),"Patch Management")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'scan_machine': default,  # # SaaS Prompts. Must fix.
            'patch_status': '',
            'initial_update': '',
            'pre_post_procedure': '',
            'automatic_update': '',
            'machine_history': '',
            # Manage updates
            'machine_updates': '',
            'patch_updates': '',
            'rollback': '',
            'cancel_updates': '',
            # Patch policy
            'create_delete': '',
            'membership': '',
            'approval_by_policy': '',
            'approval_by_patch': '',
            'kb_override': '',
            # Configure
            'windows_auto_update': '',
            'reboot_action': '',
            'file_src': '',
            'patch_alert': '',
            'office_src': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def policy_mgmt(driver, location=''):
    default = '//h3[contains(text(),"Policy Management")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
            'dashboard': '',
            'logs': '',
            'policy_matrix': '',
            # Configure
            'policies': '',
            'settings': '',
            # Assignment
            'orgs_mach_grps': '',
            'machines': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def remote_control(driver, location=''):
    default = '//h3[contains(text(),"Remote Control")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'control_machine': default,
            'reset_password': '',
            # Configure
            'select_type': '',
            'set_parameters': '',
            'preinstall_rc': '',
            'uninstall_rc': '',
            # Policy Settings
            'user_role_policy': '',
            'machine_policy': '',
            # Files/Processes
            'ftp': '',
            'ssh': '',
            'task_mgr': '',
            # Message Users
            'chat': '',
            'send_msg': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def security(driver, location=''):
    default = '//h3[contains(text(),"Security")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'dashboard': default,
            'security_status': '',
            'manual_update': '',
            'schedule_scan': '',
            'view_threats': '',
            'view_logs': '',
            # License
            'extend_return': '',
            'notify': '',
            # Configure
            'installations': '',
            'define_profile': '',
            'assign_profile': '',
            'log_settings': '',
            # MS Exchange
            'exchange_status': '',
            # Security Alarms
            'define_alarm_status': '',
            'apply_alarm_sets': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def service_billing(driver, location=''):
    default = '//h3[contains(text(),"Service Billing")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'status': default,
            'customres': '',
            'vendors': '',
            'sales_orders': '',
            'work_orders': '',
            'recurring_services': '',
            'procurement': '',
            'parts': '',
            'documents': '',
            'service_billing_window': '',
            # Billing and invoicing
            'general_entries': '',
            'pending_items': '',
            'past_periods': '',
            'past_invoices': '',
            # Admin
            'recurring_svcs_catalog': '',
            'resource_types': '',
            'bulk_email_mgmt': '',
            'app_logging': '',
            # Configure
            'setup': '',
            'app_settings': '',
            'lists': '',
            # Accounting Integration
            'account_mapping': '',
            'config': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def service_desk(driver, location=''):
    default = '//h3[contains(text(),"Service Desk")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'tickets': default,
            'org_tickets': '',
            'tasks_assoc_tickets': '',
            'archived_tickets': '',
            'knowledge_base': '',
            'search_all': '',
            # Desk Config
            'desk_definition': '',
            # Templates
            'desk_templates': '',
            'note_templates': '',
            'msg_templates': '',
            # Common Config
            'global_settings': '',
            'role_preferences': '',
            'user_preferences': '',
            'inc_email_alarm_': '',
            'procedure_variables': '',
            'policies': '',
            'coverage_schedules': '',
            'holidays': '',
            # Procedures Definition
            'stage_entry_exit': '',
            'ticket_change': '',
            'ticket_req_dedup': '',
            'ticket_req_mapping': '',
            'goal': '',
            'escalation': '',
            'sub_proceures': '',
            # Admin
            'app_logging': '',
            'resend_time_entries': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def software_deployment(driver, location=''):
    default = '//h3[contains(text(),"Software Deployment")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
            'dashboard': '',
            'deployment_analysis': '',
            'schedules': '',
            'archived_alerts': '',
            # Status
            'status_machine': '',
            'status_software_title': '',
            'pending_approvals': '',
            # Manual Deployment
            'manual_machine': '',
            'manual_software_title': '',
            # Profiles
            'manage': '',
            'assign_by_machine': '',
            'assign_by_profile': '',
            # Configure
            'catalog': '',
            'app_settings': '',
            'alerts': '',
            'reboot_actions': '',
            'setup': '',
            'file_src': '',
            'file_src_machine': '',
            # Admin
            'app_logging': '',
            'licensing': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def software_mgmt(driver, location=''):
    default = '//h3[contains(text(),"Software Management")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'dashboard': default,
            'machines': '',
            'patch_approval': '',
            'vulnerabilities': '',
            'patch_history': '',
            # Profiles
            'scan_analysis': '',
            'override': '',
            '3rd_party_software': '',
            'deployment': '',
            'alerting': '',
            # Config
            'settings': '',
            # Admin
            'app_logging': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def system(driver, location=''):
    default = '//h3[text()="System"]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'preferences': default,
            'change_logon': '',
            # Preferences
            'naming_policy': '',
            # User Security
            'users': '//*[contains(@data-nav-id,"10223")]',
            'user_roles': '',
            'machine_roles': '',
            'scopes': '',
            'logon_hours': '',
            'user_history': '',
            # Org/Grp/Dept/Staff
            'manage': '',
            'set_up_types': '//*[contains(@data-nav-id,"10018")]',
            # Server Management
            'default_settings': '',
            'license_manager': '',
            'import_center': '//*[contains(@data-nav-id,"10171")]',
            'system_log': '',
            'logon_policy': '',
            'outbound_email': '',
            'oauth_clients': '',
            # Customize
            'site_customization': '//*[contains(@data-nav-id,"10512")]',
            'local_settings': '',
            'live_connect': '',
            'it_glue': '',
            # BMS
            'sync_config': '',
            'sync_transactions': '',
            'bms_api_log': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def system_backup_recovery(driver, location=''):
    default = '//h3[contains(text(),"System Backup and Recovery")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
            'dashboard': '',
            'status': '',
            # Images
            'mount': '',
            'backup_hist': '',
            # Profiles
            'manage': '',
            'assign_by_machine': '',
            'assign_by_profile': '',
            # Configure
            'alerts': '',
            'install_remove': '',
            # Admin
            'app_logging': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print('Unable to match location provided. Trying default...')
            return default
    return default


def ticketing(driver, location=''):
    default = '//h3[contains(text(),"Ticketing")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'view_summary': default,
            'create_view': '',
            'delete_archive': '',
            'migrate_tickets': '',
            # Configure
            'notify_policy': '',
            'access_policy': '',
            'assignee_policy': '',
            'due_date_policy': '',
            'edit_fields': '',
            'email_reader': '',
            'email_mapping': '',
        }
        if location in locations.keys:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def time_tracking(driver, location=''):
    default = '//h3[contains(text(),"Time Tracking")]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'dashboard': default,
            # Time sheets
            'my_time_sheets': '',
            'approve_time_sheets': '',
            'time_sheet_summary': '',
            'unprocessed_transactions': '',
            'app_logging': '',
            'time_sheet_hist_summary': '',
            'time_sheet_hist_details': '',
            # Configure
            'settings': '',
            'periods': '',
            'admin_tasks': '',
            'approval_patterns': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default


def vpro(driver, location=''):
    default = '//h3[text()="vPro"]'
    if not panel_open(driver):
        panel_open(driver)
    if location:
        locations = {
            'overview': default,
            # Setup
            'automated': '',
            'vpro_proxy': '',
            'manage_boot_iso': '',
            'detect_activate': '',
            'wireless': '',
            'alerts': '',
            # vPro actions
            'power': '',
            'remote_control': '',
            'remote_drive_mount': '',
            'secure_erase': '',
            # Admin
            'logs': '',
        }
        if location in locations:
            return locations.get(location)
        else:
            print_err()
            return default
    return default
