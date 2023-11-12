import json
import os
import sys
import webbrowser

import PySimpleGUI as sg

bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
# path_to_json = os.path.abspath(os.path.join(bundle_dir, "vcenter_envs.json"))

ovf_tool_link = "https://developer.vmware.com/web/tool/4.6.2/ovf-tool/"
current_envs = {}
manage_window = None
font = ("Courier New", 14, "underline")


def get_latest_envs():
    with open(f"{bundle_dir}/vcenter_envs.json", "r") as env_file:
        global current_envs
        current_envs = json.load(env_file)


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
                sg.Text("vCenter Environemnt:"),
                sg.Combo(
                    list(current_envs.keys()),
                    s=25,
                    readonly=True,
                    key="envs",
                    enable_events=True,
                ),
            ],
            [sg.Text("vCenter IP:"), sg.Input("10.1.1.1", s=25, key="vc_ip")],
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
                sg.Text("VM-Network 1:", size=10),
                sg.Input("", size=(None, 20), key="vc_nw1"),
            ],
            [
                sg.Text("VM-Network 2:", size=10),
                sg.Input("", size=(None, 20), key="vc_nw2"),
            ],
            [
                sg.Text("VM-Network 3:", size=10),
                sg.Input("", size=(None, 20), key="vc_nw3"),
            ],
            [
                sg.Text("Datastore", size=10),
                sg.Input("", size=(None, 20), key="vc_storage"),
            ],
        ]
    ),
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
]
window = sg.Window("Deploy OVA", layout, finalize=True)


def open_window():
    get_latest_envs()
    envs = list(current_envs.keys())
    new_vc_layout = [
        sg.Column(
            layout=[
                [
                    sg.Text("vCenter IP:"),
                    sg.Input(size=20, key="manage_vc_ip"),
                ],
                [
                    sg.Text("Username:"),
                    sg.Input(
                        "Administrator@vsphere.local", size=25, key="manage_vc_username"
                    ),
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
                    sg.Input("10.1.1.1", size=(None, 20), key="manage_vc_gateway"),
                ],
                [
                    sg.Text("DNS:", size=10),
                    sg.Input("10.1.2.1", size=(None, 20), key="manage_vc_dns"),
                ],
                [
                    sg.Text("Subnet:", size=10),
                    sg.Input("255.255.255.0", size=(None, 20), key="manage_vc_subnet"),
                ],
            ]
        ),
        sg.Column(
            layout=[
                [
                    sg.Text("VM-Network 1:", size=10),
                    sg.Input("10.1.1.1", size=(None, 20), key="manage_vc_nw1"),
                ],
                [
                    sg.Text("VM-Network 2:", size=10),
                    sg.Input("10.1.2.1", size=(None, 20), key="manage_vc_nw2"),
                ],
                [
                    sg.Text("VM-Network 3:", size=10),
                    sg.Input("255.255.255.0", size=(None, 20), key="manage_vc_nw3"),
                ],
                [
                    sg.Text("Datastore", size=10),
                    sg.Input("255.255.255.0", size=(None, 20), key="manage_vc_storage"),
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
                default_value="Select vCenter Environment",
                size=30,
                enable_events=True,
                key="manage_env",
            )
        ],
        [sg.Button("Save"), sg.Button("Delete", button_color="white on red")],
        new_vc_layout,
    ]
    global manage_window
    manage_window = sg.Window("Manage Environment", manage_layout, modal=True)
    while True:
        event, values = manage_window.read()
        print(event)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "manage_env":
            vc_env = values["manage_env"]
            change_values(vc_env, manage_env=True)

    manage_window.close()


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
    elif event.startswith("-OVF-URL-"):
        webbrowser.open(ovf_tool_link)
    print(event, values)

window.close()
