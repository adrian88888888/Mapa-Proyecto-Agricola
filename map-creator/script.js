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
            icon_size = 10;
            break;
        case 8:
            icon_size = 10;
            break;
        case 9:
            icon_size = 10;
            break;
        case 10:
            icon_size = 10;
            break;
        case 11:
            icon_size = 10;
            break;
        case 12:
            icon_size = 15;
            break;
        case 13:
            icon_size = 23;
            break;
        case 14:
            icon_size = 30;
            break;
        case 15:
            icon_size = 33;
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
    console.log('zoom: ', zoom);
    // icon_size = icon_size + 10
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

function onMapClick(e) {
    var zoom = map.getZoom();
    if (zoom >= 16) {
        var lat = e.latlng.lat;
        var lng = e.latlng.lng;
        var coords = `${lat}, ${lng}`;
        var popupContent = `
            <div>
                <a href="#" onclick="navigator.clipboard.writeText('${coords}').catch(err => { console.error('Error al copiar', err); }); return false;">
                    ✂️ Copiar coordenadas ✂️
                </a>
            </div>
        `;
        // var wwp_mesage_new_client = `https://wa.me/+59895930076?text=Adriano, en estas coordenadas hay un cliente nuevo:${lat},${lng}`;
        // var wwp_mesage_share_coords = `https://wa.me/+59895930076?text=${lat},${lng}`;
        // var popupContent = `
        //     <div>
        //         <a href="${wwp_mesage_new_client}" target="_blank">➕Crear cliente en este punto</a><br><br>
        //         <a href="${wwp_mesage_share_coords}" target="_blank">🔁Compartir este punto</a>
        //     </div>
        // `;
        
        var popup = L.popup()
            .setLatLng(e.latlng)
            .setContent(popupContent)
            .openOn(map);
    }
}

map.on('click', onMapClick);
