import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import QtQuick.Dialogs
import RinUI
import "qrc:/resources/ui/components"

FluentPage {
    id: root
    title: "Integration"

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 8

        SettingExpander {
            icon.name : "ic_fluent_play_circle_hint_20_regular"
            Layout.fillWidth: true
            title: qsTr("Custom Launch Splash")
            description: qsTr("Create or use your own custom Splash when launching sober with Chroma! Notice that this will not work with bloxstrap one.")
            icon.size: 28

            SettingItem {
                title: qsTr("Set Custom Launch Splash")

                ComboBox {
                    property var data : Backend.getSplash()
                    property bool initialized: false

                    model: Backend.getSplash()

                    Component.onCompleted: {
                        currentIndex = data.indexOf(Backend.getCurrentSplash())
                        initialized = true
                    }

                    onCurrentIndexChanged: {
                        if (initialized) {
                            Backend.setSplash(data[currentIndex])
                        }
                    }
                }
            }

            SettingItem {
                title: qsTr("See how to make one")

                Hyperlink {
                    text: qsTr("Click here")
                    openUrl: "https://github.com/Wookhq/Lution"
                }
            }
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 8

        Text {
            typography: Typography.BodyStrong
            text: "Sober"
        }

        SettingExpander {
            icon.name : "ic_fluent_plug_disconnected_20_regular"
            Layout.fillWidth: true
            title: qsTr("Discord RPC")
            description: qsTr("Display your roblox game status on Discord via Discord RPC")
            icon.size: 28

            SettingItem {
                title: qsTr("Enable?")

                Switch {}
            }

            SettingItem {
                title: qsTr("Show join button")
                description: qsTr("Discord RPC is required in order to enable this feature")

                Switch {

                }
            }
        }

        SettingCard {
            Layout.fillWidth: true
            title: qsTr("Close on leave")
            description: qsTr("Close sober on leave")
            icon.name: "ic_fluent_tab_desktop_arrow_left_20_regular"
            content:    Switch {}
        }

        SettingCard {
            Layout.fillWidth: true
            title: qsTr("Enable HIDPI")
            icon.name: "ic_fluent_share_screen_person_20_regular"
            content:    Switch {}
        }

        SettingCard {
            Layout.fillWidth: true
            title: qsTr("Graphics optimization mode")
            description: qsTr("Quality : Roblox delivers desktop-level graphics and visual fidelity; this is the default setting. ; Balanced : Roblox maintains a balance between visual quality and performance. ; Performance : Roblox prioritizes performance over graphics quality, resulting in reduced LOD detail and lower texture quality.")
            icon.name: "ic_fluent_desktop_edit_20_regular"
            content: ComboBox {
                model: ListModel {
                    ListElement { text: qsTr("Quality") }
                    ListElement { text: qsTr("Balanced") }
                    ListElement { text: qsTr("Performance") }
                }

                onCurrentIndexChanged: {
                    console.log(model.get(currentIndex).text)
                }
            }
        }
    }
}
