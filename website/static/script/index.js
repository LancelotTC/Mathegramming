function eraseAll(notifId) {
	fetch(
		"/clear_all_notifications",
		{ method: "POST", body: JSON.stringify({ notifId: notifId }) })
		.then((_res) => { window.location.href = ""; })
}

