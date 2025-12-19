import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import "qrc:/resources/ui/components/marketplace/"

FluentPage {
    id: root
    title: "Marketplace"

    ListModel {
        id: clipModel
        ListElement { title: "cool clip #1"; desc: "2025-01-01"}
        ListElement { title: "banger clip #2"; desc: "2025-01-02" }
        ListElement { title: "mid clip #3"; desc: "2025-01-03" }
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
