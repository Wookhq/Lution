import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI
import "qrc:/resources/ui/components/"

FluentPage {
    title: qsTr("Credits & Contributors")

    ScrollView {
        id: scroll
        anchors.fill: parent
        clip: true

        ColumnLayout {
            width: scroll.availableWidth   
            spacing: 16

            GridView {
                id: creditsGrid

                width: scroll.availableWidth   
                implicitHeight: cellHeight * 2
                clip: true

                flow: GridView.FlowTopToBottom

                cellWidth: 360
                cellHeight: 190

                model: ListModel {
                    ListElement {
                        title: "Chip"
                        desc: qsTr("Lead developer")
                        img: "qrc:/placeholder"
                        url: "https://github.com/whoschip"
                    }
                    ListElement {
                        title: "DIM"
                        desc: qsTr("Build script")
                        img: "qrc:/DIM"
                        url: "https://github.com/dim-ghub"
                    }
                    ListElement {
                        title: "Dreak"
                        desc: qsTr("Username detection rely on logs")
                        img: "qrc:/Dreak"
                        url: "https://github.com/helloplauz10"
                    }
                    ListElement {
                        title: "TripleAn"
                        desc: qsTr("Made the base.apk extract thinggy")
                        img: "qrc:/Placeholder"
                        url: "https://github.com/triplean"
                    }
                    ListElement {
                        title: "Foststrap Team"
                        desc: qsTr("Mod generator, forked and made sober-only")
                        img: "qrc:/Froststrap"
                        url: "https://github.com/RealMeddsam/Froststrap"
                    }
                }

                delegate: CreditCard {
                    width: creditsGrid.cellWidth
                    height: creditsGrid.cellHeight

                    title: model.title
                    desc: model.desc
                    img: model.img
                    url: model.url
                }
            }

            Text {
                text: qsTr("Code & Reference")
                font.pixelSize: 18
                leftPadding: 8
            }

            Hyperlink {
                text: "RinUI"
                openUrl: "https://github.com/RinLit-233-shiroko/Rin-UI"
                leftPadding: 8
            }
        }
    }
}
