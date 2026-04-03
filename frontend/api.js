(function () {
  window.FMS_API_BASE = window.FMS_API_BASE || "https://financial-management-system-rtrp-2.onrender.com";

  function formatDetail(detail) {
    if (detail == null) return "Request failed";
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map(function (d) {
          return d.msg || JSON.stringify(d);
        })
        .join(" ");
    }
    return "Request failed";
  }

  window.fmsApiPost = async function fmsApiPost(path, body) {
    const res = await fetch(FMS_API_BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    let data = {};
    try {
      data = await res.json();
    } catch (_) {
      /* ignore */
    }
    if (!res.ok) {
      const msg = formatDetail(data.detail);
      throw new Error(msg);
    }
    return data;
  };

  window.fmsStorage = {
    USER_ID: "fms_user_id",
    USERNAME: "fms_username",
    getUserId: function () {
      const id = localStorage.getItem(this.USER_ID);
      return id ? parseInt(id, 10) : null;
    },
    setSession: function (userId, username) {
      localStorage.setItem(this.USER_ID, String(userId));
      if (username) localStorage.setItem(this.USERNAME, username);
    },
    clear: function () {
      localStorage.removeItem(this.USER_ID);
      localStorage.removeItem(this.USERNAME);
    },
  };
})();
