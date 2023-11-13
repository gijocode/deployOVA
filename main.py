import json
import os
import subprocess
import sys
import webbrowser

import PySimpleGUI as sg

bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
# path_to_json = os.path.abspath(os.path.join(bundle_dir, "vcenter_envs.json"))

ovf_tool_link = "https://developer.vmware.com/web/tool/4.6.2/ovf-tool/"
current_envs = {}
manage_window = None
font = ("Courier New", 12, "underline")
sg.theme("LightGrey1")


def get_latest_envs():
    with open(f"{bundle_dir}/vcenter_envs.json", "r") as env_file:
        global current_envs
        current_envs = json.load(env_file)


def save_current_envs():
    with open(f"{bundle_dir}/vcenter_envs.json", "w") as env_file:
        json.dump(current_envs, env_file, indent=4)
    get_latest_envs()


def update_current_env(vc_env, values):
    current_envs[vc_env]["ip"] = values["manage_vc_ip"]
    current_envs[vc_env]["username"] = values["manage_vc_username"]
    current_envs[vc_env]["pwd"] = values["manage_vc_pwd"]
    current_envs[vc_env]["gateway"] = values["manage_vc_gateway"]
    current_envs[vc_env]["dns"] = values["manage_vc_dns"]
    current_envs[vc_env]["subnet"] = values["manage_vc_subnet"]
    current_envs[vc_env]["vmn1"] = values["manage_vc_nw1"]
    current_envs[vc_env]["vmn2"] = values["manage_vc_nw2"]
    current_envs[vc_env]["vmn3"] = values["manage_vc_nw3"]
    current_envs[vc_env]["datastore"] = values["manage_vc_storage"]
    ip_list = [v.strip() for v in values["manage_vc_iplist"].split("\n")]
    current_envs[vc_env]["ip_list"] = ip_list
    save_current_envs()
    change_values(vc_env)


def create_new_env(env_name):
    global current_envs
    if env_name not in list(current_envs.keys()):
        current_envs[env_name] = dict(
            {
                "ip": "",
                "username": "",
                "pwd": "",
                "gateway": "",
                "dns": "",
                "subnet": "",
                "vmn1": "",
                "vmn2": "",
                "vmn3": "",
                "datastore": "",
                "ip_list": ["123.234.345.123 myfqdn.mydomain.net"],
            },
        )
        save_current_envs()
        return True
    return False


get_latest_envs()
menu_row_layout = [
    [
        "vCenter Environments",
        [
            "Manage",
            "Exit",
        ],
    ],
    [
        "Help",
        [
            "How to use",
            "About",
        ],
    ],
]
vc_layout = [
    sg.Column(
        layout=[
            [
                sg.Text("vCenter Environment:"),
                sg.Combo(
                    list(current_envs.keys()),
                    s=25,
                    readonly=True,
                    key="envs",
                    default_value="--Select vCenter Environment--",
                    enable_events=True,
                ),
            ],
            [sg.Text("vCenter IP:"), sg.Input("", s=25, key="vc_ip")],
            [
                sg.Text("Username:"),
                sg.Input("", size=25, key="vc_username"),
            ],
            [
                sg.Text("Password:"),
                sg.Input(password_char="*", size=(None, 20), key="vc_pwd"),
            ],
        ]
    ),
    sg.Column(
        layout=[
            [
                sg.Text("Gateway:", size=10),
                sg.Input("", size=(None, 20), key="vc_gateway"),
            ],
            [
                sg.Text("DNS:", size=10),
                sg.Input("", size=(None, 20), key="vc_dns"),
            ],
            [
                sg.Text("Subnet:", size=10),
                sg.Input("", size=(None, 20), key="vc_subnet"),
            ],
        ]
    ),
    sg.Column(
        layout=[
            [
                sg.Text("VM-Network 1:", size=12),
                sg.Input("", size=(None, 20), key="vc_nw1"),
            ],
            [
                sg.Text("VM-Network 2:", size=12),
                sg.Input("", size=(None, 20), key="vc_nw2"),
            ],
            [
                sg.Text("VM-Network 3:", size=12),
                sg.Input("", size=(None, 20), key="vc_nw3"),
            ],
            [
                sg.Text("Datastore:", size=12),
                sg.Input("", size=(None, 20), key="vc_storage"),
            ],
        ]
    ),
]
vm_layout = [
    [
        sg.Column(
            vertical_alignment="top",
            layout=[
                [
                    sg.Text("VM Name:", size=10),
                    sg.Input("", size=(None, 20), key="vm_name"),
                ],
                [
                    sg.Text("IP & FQDN:", size=10),
                ],
                [
                    sg.Combo(
                        values=[],
                        default_value="--Select--",
                        size=35,
                        auto_size_text=True,
                        key="vm_ip_fqdn",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Power On after deploying", key="vm_power", default=True
                    ),
                ],
            ],
        ),
        sg.Column(
            layout=[
                [
                    sg.Multiline(
                        "Ping Output",
                        expand_y=True,
                        autoscroll=True,
                        size=30,
                        background_color="black",
                        expand_x=True,
                        text_color="white",
                        font="monospace 10",
                        auto_refresh=True,
                        key="ping_output",
                        horizontal_scroll=True,
                    ),
                ],
            ],
            vertical_alignment="top",
            expand_y=True,
            expand_x=True,
        ),
        sg.Column(
            layout=[
                [
                    sg.Multiline(
                        "Nslookup Output",
                        size=30,
                        autoscroll=True,
                        expand_y=True,
                        expand_x=True,
                        background_color="black",
                        horizontal_scroll=True,
                        text_color="white",
                        font="monospace 10",
                        key="nslookup_output",
                        auto_refresh=True,
                    ),
                ],
            ],
            vertical_alignment="top",
            expand_y=True,
            expand_x=True,
        ),
    ],
]
layout = [
    [sg.Menu(menu_row_layout)],
    [  # Remove this if you will package the ovftool within the exe
        sg.Text(
            "Before you proceed, make sure you install the ovf tool and add it to your System Path",
            auto_size_text=True,
        ),
        sg.Text(
            "VMware OVF tool",
            tooltip=ovf_tool_link,
            enable_events=True,
            font=font,
            key="-OVF-URL-",
        ),
    ],
    [
        sg.Text("Select the ova file"),
        sg.FileBrowse("Browse", target="test", enable_events=True),
        sg.Text("", key="test", enable_events=True),
    ],
    [
        sg.Frame("vCenter where ova should be deployed:", layout=[vc_layout]),
    ],
    [
        sg.Frame(
            "VM Settings",
            layout=vm_layout,
            expand_x=True,
            size=(20, 150),
            expand_y=True,
        ),
    ],
]
window = sg.Window(
    "Deploy OVA",
    layout,
    finalize=True,
    resizable=True,
    auto_size_text=True,
    auto_size_buttons=True,
)


def open_window():
    get_latest_envs()
    envs = list(current_envs.keys())
    fqdn_ip_layout = [
        sg.Column(
            layout=[
                [
                    sg.Text(
                        "In the below textfield, enter the list of IP and FQDN pairs you will be using for this environemnt to deploy VMs.\nThe IP and FQDN must be space separated. An example is already filled in. \nEach line must contain exactly 1 entry."
                    ),
                ],
                [
                    sg.Multiline(
                        default_text="123.234.345.123 myfqdn.mydomain.net",
                        size=(None, 15),
                        font="monospace 12",
                        key="manage_vc_iplist",
                    ),
                ],
            ],
            pad=0,
        )
    ]
    new_vc_layout = [
        sg.Column(
            layout=[
                [
                    sg.Text("vCenter IP:"),
                    sg.Input(size=20, key="manage_vc_ip"),
                ],
                [
                    sg.Text("Username:"),
                    sg.Input("", size=25, key="manage_vc_username"),
                ],
                [
                    sg.Text("Password:"),
                    sg.Input(password_char="*", size=(None, 20), key="manage_vc_pwd"),
                ],
            ]
        ),
        sg.Column(
            layout=[
                [
                    sg.Text("Gateway:", size=10),
                    sg.Input("", size=(None, 20), key="manage_vc_gateway"),
                ],
                [
                    sg.Text("DNS:", size=10),
                    sg.Input("", size=(None, 20), key="manage_vc_dns"),
                ],
                [
                    sg.Text("Subnet:", size=10),
                    sg.Input("", size=(None, 20), key="manage_vc_subnet"),
                ],
            ]
        ),
        sg.Column(
            layout=[
                [
                    sg.Text("VM-Network 1:", size=13),
                    sg.Input("", size=(None, 20), key="manage_vc_nw1"),
                ],
                [
                    sg.Text("VM-Network 2:", size=13),
                    sg.Input("", size=(None, 20), key="manage_vc_nw2"),
                ],
                [
                    sg.Text("VM-Network 3:", size=13),
                    sg.Input("", size=(None, 20), key="manage_vc_nw3"),
                ],
                [
                    sg.Text("Datastore", size=10),
                    sg.Input("", size=(None, 20), key="manage_vc_storage"),
                ],
            ]
        ),
    ]
    manage_layout = [
        [
            sg.Text("Manage vCenter Environments"),
        ],
        [
            sg.Combo(
                envs,
                default_value="--Select vCenter Environment--",
                size=30,
                enable_events=True,
                key="manage_env",
            ),
            sg.Text("OR"),
            sg.Button("Create new Environment", key="create_env"),
        ],
        new_vc_layout,
        fqdn_ip_layout,
        [
            sg.Button("Save", key="save_env"),
            sg.Button("Delete", button_color="white on red", key="delete_env"),
        ],
    ]
    global manage_window
    manage_window = sg.Window("Manage Environment", manage_layout, modal=True)
    while True:
        event, values = manage_window.read()
        print(event, values)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "manage_env":
            vc_env = values["manage_env"]
            change_values(vc_env, manage_env=True)
        elif event == "create_env":
            new_env_name = sg.popup_get_text(
                "Enter a name for the environemnt", title="Create new Environment"
            )
            created = create_new_env(new_env_name)
            if created:
                sg.popup_no_buttons(
                    f"Created new environment with name {new_env_name}. You can find it in the dropdown",
                    auto_close=True,
                    title="Created!",
                )
                clear_values()
            else:
                sg.popup_no_buttons(
                    f"Environment with name {new_env_name} already exists, you can find it in the dropdown"
                )
        elif event == "delete_env":
            vc_env = values["manage_env"]
            ch = sg.popup_yes_no(
                f"Are you sure you want to delete '{vc_env}'?",
                title="Need Confirmation",
            )
            if ch == "Yes":
                del current_envs[vc_env]
                save_current_envs()
                clear_values()
        elif event == "save_env":
            vc_env = values["manage_env"]
            update_current_env(vc_env, values)
            sg.popup_no_buttons(f"Updated Environment '{vc_env}'", title="Success!")

    manage_window.close()


def clear_values():
    manage_window.find_element("manage_vc_ip").update("")
    manage_window.find_element("manage_vc_username").update("")
    manage_window.find_element("manage_vc_pwd").update("")
    manage_window.find_element("manage_vc_gateway").update("")
    manage_window.find_element("manage_vc_dns").update("")
    manage_window.find_element("manage_vc_subnet").update("")
    manage_window.find_element("manage_vc_nw1").update("")
    manage_window.find_element("manage_vc_nw2").update("")
    manage_window.find_element("manage_vc_nw3").update("")
    manage_window.find_element("manage_vc_storage").update("")
    manage_window.find_element("manage_env").update(
        values=list(current_envs.keys()), value="--Select vCenter Environment--"
    )


def change_values(vc_env, manage_env=False):
    if manage_env:
        manage_window.find_element("manage_vc_ip").update(current_envs[vc_env]["ip"])
        manage_window.find_element("manage_vc_username").update(
            current_envs[vc_env]["username"]
        )
        manage_window.find_element("manage_vc_pwd").update(current_envs[vc_env]["pwd"])
        manage_window.find_element("manage_vc_gateway").update(
            current_envs[vc_env]["gateway"]
        )
        manage_window.find_element("manage_vc_dns").update(current_envs[vc_env]["dns"])
        manage_window.find_element("manage_vc_subnet").update(
            current_envs[vc_env]["subnet"]
        )
        manage_window.find_element("manage_vc_nw1").update(current_envs[vc_env]["vmn1"])
        manage_window.find_element("manage_vc_nw2").update(current_envs[vc_env]["vmn2"])
        manage_window.find_element("manage_vc_nw3").update(current_envs[vc_env]["vmn3"])
        manage_window.find_element("manage_vc_storage").update(
            current_envs[vc_env]["datastore"]
        )
        manage_window.find_element("manage_vc_iplist").update(
            "\n".join(current_envs[vc_env]["ip_list"])
        )
        manage_window.find_element("manage_env").update(
            values=list(current_envs.keys()), value=vc_env
        )
    window.find_element("envs").update(values=list(current_envs.keys()), value=vc_env)
    window.find_element("vc_ip").update(current_envs[vc_env]["ip"])
    window.find_element("vc_username").update(current_envs[vc_env]["username"])
    window.find_element("vc_pwd").update(current_envs[vc_env]["pwd"])
    window.find_element("vc_gateway").update(current_envs[vc_env]["gateway"])
    window.find_element("vc_dns").update(current_envs[vc_env]["dns"])
    window.find_element("vc_subnet").update(current_envs[vc_env]["subnet"])
    window.find_element("vc_nw1").update(current_envs[vc_env]["vmn1"])
    window.find_element("vc_nw2").update(current_envs[vc_env]["vmn2"])
    window.find_element("vc_nw3").update(current_envs[vc_env]["vmn3"])
    window.find_element("vc_storage").update(current_envs[vc_env]["datastore"])
    window.find_element("envs").update(values=list(current_envs.keys()), value=vc_env)
    window.find_element("vm_ip_fqdn").update(
        values=current_envs[vc_env]["ip_list"], value="--Select--"
    )


def perform_ip_checks(ip, fqdn):
    ip = ip.strip()
    ping_op_element = window.find_element("ping_output")
    nslookup_op_element = window.find_element("nslookup_output")
    ping_str = f">ping {ip}\n"
    nslookup_str = f">nslookup {ip}\n"

    ping_op_element.update(ping_str)
    nslookup_op_element.update(nslookup_str)
    ping_op = subprocess.run(
        ["ping", "-c", "3", ip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        # capture_output=True,
    )
    nslookup = subprocess.run(["nslookup", ip], stdout=subprocess.PIPE, text=True)
    ping_op_element.update(ping_str + (ping_op.stdout or ping_op.stderr))
    nslookup_op_element.update(nslookup_str + nslookup.stdout)


while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Manage":
        open_window()
    elif event == "envs":
        vCenter_Environment = values["envs"]
        change_values(vCenter_Environment)
    elif event == "vm_ip_fqdn":
        ip, fqdn = values["vm_ip_fqdn"].split(" ")
        perform_ip_checks(ip, fqdn)
    elif event.startswith("-OVF-URL-"):
        webbrowser.open(ovf_tool_link)
    print(event, values)

window.close()
