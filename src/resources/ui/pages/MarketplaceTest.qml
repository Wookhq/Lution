import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import "qrc:/resources/ui/components/marketplace/"

FluentPage {
    id: root
    title: "Marketplace"


    Component.onCompleted: {
        Backend.getMarketplaceItems()
    }

    ListModel {
        id: clipModel
    }

    Connections {
        target: Backend
        function onMarketplaceReady(list) {
            clipModel.clear()
            for (var i = 0; i < list.length; i++) {
                clipModel.append(list[i])
            }
        }
    }

   ScrollView {
    Layout.fillWidth: true
    Layout.fillHeight: true
    padding: 12

    GridView {
        width: parent.width
        height: contentHeight

        model: clipModel
        cellWidth: 360   // 260 + spacing
        cellHeight: 240  // 140 + spacing

        delegate: ItemCard {
            width: 340
            height: 220

            title: model.title
            desc: model.desc
            img: model.img
        }
    }
}

}
