import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import QtQuick.Dialogs
import RinUI
import "qrc:/resources/ui/components"

FluentPage {
    id: root
    title: "Mods"

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            BigClip {
                title: qsTr("Open Mods Folder")
                onActivated: Backend.openModFolder()
                description: qsTr("Open the local folder where mods are stored")
                iconName: "ic_fluent_folder_20_regular"
            }

            BigClip {
                title: qsTr("See how to use mods")
                description: qsTr("Open the bloxstrap's document.")

                onActivated: Backend.openInBroswer("https://bloxstraplabs.com/wiki/features/modding/")

                iconName: "ic_fluent_book_information_20_regular"
            }
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_text_font_size_20_regular"

            title: qsTr("Custom Cursor")
            description: qsTr("Change cursor to old/new")
            content: ComboBox {
                model: ["Default", "2006", "2013"]
            }
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_cursor_20_regular"

            title: qsTr("Custom Font")
            description: qsTr("Set your font to your liking!")

            content: Button {
                text: "Open File"
                anchors.centerIn: parent
                onClicked: fileDialog.open()
            }
        }

        FileDialog {
            id: fileDialog
            title: qsTr("Select a File")
            nameFilters: ["Font File (*.tff)", "All files (*.*)"]
            onAccepted: {
                console.log("Selected file: " + selectedFile);
            }
            onRejected: {
                console.log("Selection cancelled");
            }
        }
    }
}
