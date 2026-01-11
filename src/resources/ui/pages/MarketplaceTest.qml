import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../QuickPromise/promise.js" as Promise
import RinUI
import "qrc:/resources/ui/components/marketplace/"

FluentPage {
    id: root
    title: "Marketplace"
    property bool isLoading: true
    property string errorMessage: ""

    Component.onCompleted: {
        loadMarketplaceItems()
    }

    function loadMarketplaceItems() {
        isLoading = true
        errorMessage = ""

        Q.promise(function(resolve, reject) {
            function onSuccess(list) {
                Backend.marketplaceReady.disconnect(onSuccess)
                Backend.marketplaceError.disconnect(onError)
                resolve(list)
            }

            function onError(error) {
                Backend.marketplaceReady.disconnect(onSuccess)
                Backend.marketplaceError.disconnect(onError)
                reject(error)
            }

            Backend.marketplaceReady.connect(onSuccess)
            Backend.marketplaceError.connect(onError)

            Backend.getMarketplaceItems()

        }).then(function(list) {
            clipModel.clear()
            for (var i = 0; i < list.length; i++) {
                clipModel.append(list[i])
            }
            isLoading = false
            console.log("Marketplace loaded successfully:", list.length, "items")

        }).catch(function(error) {
            // Error handling
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
            width: parent.width
            height: parent.height
            contentWidth: availableWidth
            clip: true

            GridView {
                width: parent.width
                model: clipModel
                cellWidth: 260
                cellHeight: 200

                delegate: ItemCard {
                    width: 240
                    height: 180
                    title: model.title
                    desc: model.desc
                    img: model.img
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
        width: parent.width
        height: parent.height
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
                    { text: qsTr("Downloaded"), page: downloadedPage },
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
