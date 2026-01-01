import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import QtQuick.Dialogs
import "qrc:/resources/QuickPromise/promise.js" as Q
import RinUI
import "qrc:/resources/ui/components"

FluentPage {
    id: root
    title: "Mods"

    property bool isApplyingFont: false
    property int fontProgress: 0
    property string fontProgressMessage: ""

    function applyFontChange(filePath) {
        isApplyingFont = true
        fontProgress = 0
        floatLayer.createInfoBar({
            severity: Severity.Info,
            title: qsTr("Trying to set the font..."),
            position: Position.BottomRight
        })

        Q.promise(function(resolve, reject) {
            function onSuccess() {
                floatLayer.createInfoBar({
                    severity: Severity.Success,
                    title: qsTr("Success"),
                    text: qsTr("applied font"),
                    position: Position.BottomRight
                })
                Backend.fontApplied.disconnect(onSuccess)
                Backend.fontError.disconnect(onError)
                resolve()
            }

            function onError(error) {
                floatLayer.createInfoBar({
                    severity: Severity.Error,
                    title: qsTr("Something went wrong"),
                    text: qsTr("Check the logs for more info."),
                    position: Position.BottomRight
                })
                Backend.fontApplied.disconnect(onSuccess)
                Backend.fontError.disconnect(onError)
                reject(error)
            }

            Backend.fontApplied.connect(onSuccess)
            Backend.fontError.connect(onError)

            Backend.setFont(filePath)

        }).then(function() {
            isApplyingFont = false
        }).catch(function(error) {
            isApplyingFont = false
        })
    }

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
            icon.name: "ic_fluent_cursor_20_regular"
            title: qsTr("Custom Cursor")
            description: qsTr("Change cursor to old/new")
            content: ComboBox {
                model: ["Default", "2006", "2013"]
            }
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_text_font_size_20_regular"
            title: qsTr("Custom Font")
            description: qsTr("Set your font to your liking!")
            content: Button {
                text: "Open File"
                anchors.centerIn: parent
                enabled: !isApplyingFont
                onClicked: fileDialog.open()
            }
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_box_multiple_20_regular"
            title: qsTr("Open Mod genarator")
            description: qsTr("gurt")
            content: Button {
                text: "Open"
                anchors.centerIn: parent
                onClicked: window.navigationView.push(
                    Qt.resolvedUrl("ModGenarator.qml")
                )
            }
        }

        FileDialog {
            id: fileDialog
            title: qsTr("Select a File")
            nameFilters: ["Font File (*.ttf)", "All files (*.*)"]
            onAccepted: {
                console.log(selectedFile)
                applyFontChange(selectedFile)
            }
            onRejected: {
                console.log("Selection cancelled");
            }
        }
    }
}
