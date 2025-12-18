// taken from vimal's qml

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI
import "pages"
import "pages/playerlog"

FluentWindow {
    id: window
    visible: true
    width: 1200
    height: 700
    minimumWidth: 550
    minimumHeight: 400


    navigationItems: [
            {
                icon: "ic_fluent_home_20_regular",
                title: qsTr("Home"),
                page: homePage
            },
            {
                icon: "ic_fluent_shopping_bag_20_regular",
                title: qsTr("Marketplace"),
                // page: cloudPage
            },
            {
                icon : "ic_fluent_box_20_regular",
                title: qsTr("Mods"),
                page : modPage
            },
            {
                icon : "ic_fluent_flag_20_regular",
                title: qsTr("Feature flag")
            },
            {
                icon : "ic_fluent_sparkle_20_regular",
                title: qsTr("Intergation"),
                // page : intergation
            },
            {
                icon: "ic_fluent_settings_20_regular",
                title: qsTr("Settings"),
                // page: settingsPage
            }
        ]

    Component.onCompleted: Qt.callLater(function() {
        Theme.setTheme(Backend.isDark() ? Theme.mode.Dark : Theme.mode.Light) // note : impl for linux
    })


    Component { id: homePage; Home {} }
    Component { id: modPage; Mods {} }
//    Component { id: intergation; PlayerLog {} }
    // Component { id: cloudPage; Cloud {} }

}