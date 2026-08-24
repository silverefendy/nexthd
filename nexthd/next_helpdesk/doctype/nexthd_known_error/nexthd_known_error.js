// Copyright (c) 2026, nexthd and contributors
// For license information, please see license.txt

frappe.ui.form.on("NextHD Known Error", {
	refresh(frm) {
		render_photo_gallery(frm);
	},
	photos_add: function(frm) {
		render_photo_gallery(frm);
	},
	photos_remove: function(frm) {
		render_photo_gallery(frm);
	}
});

function render_photo_gallery(frm) {
	if (!frm.doc.photos || frm.doc.photos.length === 0) {
		return;
	}

	frm.fields_dict.photos.$wrapper.find('.nexthd-photo-gallery').remove();

	var gallery_html = '<div class="nexthd-photo-gallery" style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 10px;">';
	
	frm.doc.photos.forEach(function(row, index) {
		if (row.photo_preview) {
			var img_url = row.photo_preview;
			gallery_html += '<div class="nexthd-photo-thumbnail" style="width: 100px; height: 100px; cursor: pointer; border: 1px solid #d1d8dd; border-radius: 4px; overflow: hidden;" data-index="' + index + '">';
			gallery_html += '<img src="' + img_url + '" style="width: 100%; height: 100%; object-fit: cover;">';
			gallery_html += '</div>';
		}
	});
	
	gallery_html += '</div>';
	
	frm.fields_dict.photos.$wrapper.append(gallery_html);

	frm.fields_dict.photos.$wrapper.find('.nexthd-photo-thumbnail').on('click', function() {
		var index = $(this).data('index');
		open_photo_viewer(frm, index);
	});
}

function open_photo_viewer(frm, start_index) {
	var photos = frm.doc.photos || [];
	if (photos.length === 0) return;

	var current_index = start_index;
	
	var dialog = new frappe.ui.Dialog({
		title: 'Galeri Foto',
		size: 'fullscreen',
		fields: [
			{
				fieldname: 'photo_container',
				fieldtype: 'HTML',
				options: '<div id="nexthd-photo-viewer" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; background: #000; position: relative;">' +
					'<button id="nexthd-prev-btn" style="position: absolute; left: 20px; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.7); border: none; border-radius: 50%; width: 50px; height: 50px; font-size: 24px; cursor: pointer; z-index: 10;">&#10094;</button>' +
					'<img id="nexthd-current-photo" src="" style="max-width: 90%; max-height: 90vh; object-fit: contain;">' +
					'<button id="nexthd-next-btn" style="position: absolute; right: 20px; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.7); border: none; border-radius: 50%; width: 50px; height: 50px; font-size: 24px; cursor: pointer; z-index: 10;">&#10095;</button>' +
					'<div id="nexthd-photo-caption" style="color: #fff; margin-top: 10px; text-align: center;"></div>' +
					'<div id="nexthd-photo-counter" style="color: #fff; margin-top: 5px;"></div>' +
				'</div>'
			}
		]
	});

	dialog.show();

	function update_photo() {
		var photo = photos[current_index];
		var img_url = photo.photo_preview || '';
		var caption = photo.caption || '';
		
		dialog.$wrapper.find('#nexthd-current-photo').attr('src', img_url);
		dialog.$wrapper.find('#nexthd-photo-caption').text(caption);
		dialog.$wrapper.find('#nexthd-photo-counter').text((current_index + 1) + ' / ' + photos.length);
		
		dialog.$wrapper.find('#nexthd-prev-btn').toggle(current_index > 0);
		dialog.$wrapper.find('#nexthd-next-btn').toggle(current_index < photos.length - 1);
	}

	update_photo();

	dialog.$wrapper.find('#nexthd-prev-btn').on('click', function() {
		if (current_index > 0) {
			current_index--;
			update_photo();
		}
	});

	dialog.$wrapper.find('#nexthd-next-btn').on('click', function() {
		if (current_index < photos.length - 1) {
			current_index++;
			update_photo();
		}
	});

	var touch_start_x = 0;
	var touch_end_x = 0;
	var photo_img = dialog.$wrapper.find('#nexthd-current-photo')[0];

	photo_img.addEventListener('touchstart', function(e) {
		touch_start_x = e.changedTouches[0].screenX;
	}, false);

	photo_img.addEventListener('touchend', function(e) {
		touch_end_x = e.changedTouches[0].screenX;
		handle_swipe();
	}, false);

	function handle_swipe() {
		var delta_x = touch_end_x - touch_start_x;
		if (Math.abs(delta_x) > 50) {
			if (delta_x > 0) {
				if (current_index > 0) {
					current_index--;
					update_photo();
				}
			} else {
				if (current_index < photos.length - 1) {
					current_index++;
					update_photo();
				}
			}
		}
	}

	$(document).on('keydown.nexthd_photo_viewer', function(e) {
		if (e.key === 'ArrowLeft' && current_index > 0) {
			current_index--;
			update_photo();
		} else if (e.key === 'ArrowRight' && current_index < photos.length - 1) {
			current_index++;
			update_photo();
		} else if (e.key === 'Escape') {
			dialog.hide();
			$(document).off('keydown.nexthd_photo_viewer');
		}
	});

	dialog.on_hide = function() {
		$(document).off('keydown.nexthd_photo_viewer');
	};
}
