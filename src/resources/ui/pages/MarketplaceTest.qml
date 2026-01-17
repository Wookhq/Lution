import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../QuickPromise/promise.js" as Q
import RinUI
import "qrc:/resources/ui/components/marketplace/"

FluentPage {
    id: root
    title: "Marketplace"

    property bool isLoading: true
    property string errorMessage: ""

    Component.onCompleted: loadMarketplaceItems()

    function loadMarketplaceItems() {
        isLoading = true
        errorMessage = ""

        Q.promise(function (resolve, reject) {

            function onSuccess(data) {
                Backend.marketplaceReady.disconnect(onSuccess)
                Backend.marketplaceError.disconnect(onError)
                resolve(data)
            }

            function onError(error) {
                Backend.marketplaceReady.disconnect(onSuccess)
                Backend.marketplaceError.disconnect(onError)
                reject(error)
            }

            Backend.marketplaceReady.connect(onSuccess)
            Backend.marketplaceError.connect(onError)
            Backend.getMarketplaceItems()

        }).then(function (data) {
            clipModel.clear()

            if (data.Mods && data.Mods.length !== undefined) {
                for (var i = 0; i < data.Mods.length; i++) {
                    clipModel.append(data.Mods[i])
                }
                console.log("Marketplace loaded successfully:", data.Mods.length, "mods")
            } else {
                console.error("Invalid marketplace data:", data)
                errorMessage = "Invalid marketplace data"
            }

            isLoading = false

        }).catch(function (error) {
            console.error("Failed to load marketplace:", error)
            errorMessage = error || "Unknown error"
            isLoading = false
        })
    }

    ListModel {
        id: clipModel
    }


    Component {
        id: marketplacePage

        ScrollView {
            anchors.fill: parent
            clip: true

            GridView {
                anchors.fill: parent
                model: clipModel
                cellWidth: 410
                cellHeight: 240

               delegate: ItemCard {
                    width: 400
                    height: 230

                    title: model.title
                    desc: model.body
                    img: model.image
                    creator: model.creator
                    modId: model.id
                }

            }
        }
    }

    Component {
        id: downloadedPage
        Item {
            Label {
                anchors.centerIn: parent
                text: qsTr("Still working on this!!")
            }
        }
    }

    Component {
        id: loadingPage
        Item {
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 16

                ProgressRing {
                    Layout.alignment: Qt.AlignHCenter
                    indeterminate: true
                    state: ProgressRing.Running
                }

                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTr("Loading marketplace items...")
                    typography: Typography.Body
                }
            }
        }
    }

    Component {
        id: errorPage
        Item {
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 16

                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTr("Failed to load marketplace")
                    typography: Typography.Subtitle
                    color: "red"
                }

                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: errorMessage
                    typography: Typography.Body
                    wrapMode: Text.WordWrap
                }

                Button {
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTr("Retry")
                    onClicked: loadMarketplaceItems()
                }
            }
        }
    }


    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        SelectorBar {
            id: selectorBar
            Layout.fillWidth: true
            currentIndex: 0
            enabled: !isLoading

            Repeater {
                id: rep
                model: [
                    { text: qsTr("Store"), page: marketplacePage },
                    { text: qsTr("Downloaded"), page: downloadedPage }
                ]

                SelectorBarItem {
                    text: modelData.text
                }
            }
        }

        Loader {
            Layout.fillWidth: true
            Layout.fillHeight: true
            sourceComponent: {
                if (isLoading) return loadingPage
                if (errorMessage !== "") return errorPage
                return rep.model[selectorBar.currentIndex].page
            }
        }
    }
}
