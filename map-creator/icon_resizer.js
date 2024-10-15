function resizeIcons() {
    var marker = document.getElementsByClassName('leaflet-marker-icon');
    var zoom = map.getZoom();
    switch (zoom) {
        case 1:
            icon_size = 5;
            break;
        case 2:
            icon_size = 5;
            break;
        case 3:
            icon_size = 5;
            break;
        case 4:
            icon_size = 5;
            break;
        case 5:
            icon_size = 5;
            break;
        case 6:
            icon_size = 5;
            break;
        case 7:
            icon_size = 5;
            break;
        case 8:
            icon_size = 5;
            break;
        case 9:
            icon_size = 5;
            break;
        case 10:
            icon_size = 5;
            break;
        case 11:
            icon_size = 8;
            break;
        case 12:
            icon_size = 10;
            break;
        case 13:
            icon_size = 15;
            break;
        case 14:
            icon_size = 20;
            break;
        case 15:
            icon_size = 30;
            break;
        case 16:
            icon_size = 35;
            break;
        case 17:
            icon_size = 40;
            break;
        case 18:
            icon_size = 45;
            break;
        case 19:
            icon_size = 50;
            break;
    }
    // console.log('zoom: ', zoom);
    for (var i = 0; i < marker.length; i++) {
        marker[i].style.width = icon_size + 'px';
        marker[i].style.height = icon_size + 'px';
    }
}

map.on('zoomend', function() {
    resizeIcons();
});

map.on('load', function() {
    resizeIcons();
});
