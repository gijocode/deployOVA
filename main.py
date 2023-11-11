import json
import webbrowser

import PySimpleGUI as sg

ovf_tool_link = "https://developer.vmware.com/web/tool/4.6.2/ovf-tool/"
current_envs = {}
font = ("Courier New", 14, "underline")


def get_latest_envs():
    with open("vcenter_envs.json", "r") as env_file:
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
                    key="vc_id",
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
    [
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
    print(envs)
    new_vc_layout = [
        sg.Column(
            layout=[
                [
                    sg.Text("vCenter IP:"),
                    sg.Combo(["houston", "bangalore"], default_value="houston"),
                ],
                [
                    sg.Text("Username:"),
                    sg.Input("Administrator@vsphere.local", size=25),
                ],
                [
                    sg.Text("Password:"),
                    sg.Input(password_char="*", size=(None, 20)),
                ],
            ]
        ),
        sg.Column(
            layout=[
                [
                    sg.Text("Gateway:", size=10),
                    sg.Input("10.1.1.1", size=(None, 20)),
                ],
                [
                    sg.Text("DNS:", size=10),
                    sg.Input("10.1.2.1", size=(None, 20)),
                ],
                [
                    sg.Text("Subnet:", size=10),
                    sg.Input("255.255.255.0", size=(None, 20)),
                ],
            ]
        ),
        sg.Column(
            layout=[
                [
                    sg.Text("VM-Network 1:", size=10),
                    sg.Input("10.1.1.1", size=(None, 20)),
                ],
                [
                    sg.Text("VM-Network 2:", size=10),
                    sg.Input("10.1.2.1", size=(None, 20)),
                ],
                [
                    sg.Text("VM-Network 3:", size=10),
                    sg.Input("255.255.255.0", size=(None, 20)),
                ],
                [
                    sg.Text("Datastore", size=10),
                    sg.Input("255.255.255.0", size=(None, 20)),
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
                key="env",
            )
        ],
        [sg.Button("Save"), sg.Button("Delete", button_color="white on red")],
        new_vc_layout,
    ]
    manage_window = sg.Window("Manage Environment", manage_layout, modal=True)
    choice = None
    while True:
        event, values = manage_window.read()
        print(event)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    manage_window.close()


def change_values(vc_id):
    window.find_element("vc_ip").update(current_envs[vc_id]["ip"])
    window.find_element("vc_username").update(current_envs[vc_id]["username"])
    window.find_element("vc_pwd").update(current_envs[vc_id]["pwd"])
    window.find_element("vc_gateway").update(current_envs[vc_id]["gateway"])
    window.find_element("vc_dns").update(current_envs[vc_id]["ip"])
    window.find_element("vc_subnet").update(current_envs[vc_id]["ip"])
    window.find_element("vc_nw1").update(current_envs[vc_id]["vmn1"])
    window.find_element("vc_nw2").update(current_envs[vc_id]["vmn2"])
    window.find_element("vc_nw3").update(current_envs[vc_id]["vmn3"])
    window.find_element("vc_storage").update(current_envs[vc_id]["datastore"])


while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Manage":
        open_window()
    elif event == "vc_id":
        vc_id = values["vc_id"]
        change_values(vc_id)
    elif event.startswith("-OVF-URL-"):
        webbrowser.open(ovf_tool_link)
    print(event, values)

window.close()
