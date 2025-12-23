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
}
