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


    property bool isGenaratingMod: false
    property string hexColor: ""

    function genarateMod(hexColor) {
        isGenaratingMod = true
        floatLayer.createInfoBar({
            severity: Severity.Info,
            title: qsTr("Trying to genarate mod..."),
            position: Position.BottomRight
        })

        Q.promise(function(resolve, reject) {
            function onSuccess() {
                floatLayer.createInfoBar({
                    severity: Severity.Success,
                    title: qsTr("Success"),
                    text: qsTr("Successfully genarated mod!"),
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

            Backend.modGen.connect(onSuccess)
            Backend.modGenError.connect(onError)

            Backend.genarateMod(hexColor)

        }).then(function() {
            isGenaratingMod = false
        }).catch(function(error) {
            isGenaratingMod = false
        })
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 8


        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_code_20_regular"
            title: qsTr("Hex color")
            description: qsTr("Enter the hex color you want to make a mod with")
            content: TextArea {
                id: hextInput

                width: 50
                Layout.fillWidth: true
                onTextChanged : hexColor = hextInput.text
            }
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_box_multiple_20_regular"
            title: qsTr("Start genarating")
            content: Button {
                text: "Start"
                anchors.centerIn: parent
                onClicked: genarateMod(hexColor)
            }
        }
    }
}
