$(document).ready(function() {
  // Tambahkan tombol toggle untuk sidebar
  if ($('#sidebar-toggle-btn').length === 0) {
    var $toggleBtn = $('<button id="sidebar-toggle-btn" class="btn btn-default btn-sm">☰ Menu</button>');
    $('body').append($toggleBtn);
  }

  // Fungsi untuk toggle sidebar
  function toggleSidebar() {
    $('body').toggleClass('show-sidebar');
  }

  // Event listener untuk tombol toggle
  $('#sidebar-toggle-btn').on('click', toggleSidebar);

  // Tutup sidebar saat mengklik di luar sidebar
  $(document).on('click', function(event) {
    if (!$(event.target).closest('.desk-sidebar, #sidebar-toggle-btn').length) {
      $('body').removeClass('show-sidebar');
    }
  });

  // Prevent click on sidebar from closing it
  $('.desk-sidebar').on('click', function(event) {
    event.stopPropagation();
  });
});