import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    id : root
    title : "Home"

    Text {
        anchors.fill: parent
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter   
        font.pixelSize: 20
        id : wellcomeText
        text: qsTr("Welcome back!")
    }

}