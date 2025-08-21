document.getElementById('geoBtn')?.addEventListener('click', () => {
  if (!navigator.geolocation) {
    alert('Geolocation not supported');
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      document.getElementById('lat').value = pos.coords.latitude.toFixed(5);
      document.getElementById('lon').value = pos.coords.longitude.toFixed(5);
      document.getElementById('city').value = "";
      document.getElementById('searchForm').submit();
    },
    (err) => { alert('Unable to get location: ' + err.message); },
    { enableHighAccuracy: true, timeout: 10000 }
  );
});

