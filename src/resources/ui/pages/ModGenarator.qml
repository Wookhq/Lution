import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import QtQuick.Dialogs
import "qrc:/resources/QuickPromise/promise.js" as Q
import RinUI
import "qrc:/resources/ui/components"

FluentPage {
    id: root
    title: "Mod Genarator"

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 8


        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_code_20_regular"
            title: qsTr("Hex color")
            description: qsTr("Enter the hex color you want to make a mod with")
            content: TextArea {
                width: 50
                Layout.fillWidth: true
            }
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_box_multiple_20_regular"
            title: qsTr("Start genarating")
            content: Button {
                text: "Start"
                anchors.centerIn: parent
            }
        }
    }
}
