const STORAGE_PREFIX = "ttl";

export const storageEngine = {
  set(key, value) {
    try {
      localStorage.setItem(
        `${STORAGE_PREFIX}:${key}`,
        JSON.stringify(value)
      );
    } catch (error) {
      console.error(
        "Storage write failed:",
        error
      );
    }
  },

  get(key, fallback = null) {
    try {
      const value = localStorage.getItem(
        `${STORAGE_PREFIX}:${key}`
      );

      return value
        ? JSON.parse(value)
        : fallback;
    } catch (error) {
      console.error(
        "Storage read failed:",
        error
      );

      return fallback;
    }
  },

  remove(key) {
    localStorage.removeItem(
      `${STORAGE_PREFIX}:${key}`
    );
  },

  clear() {
    Object.keys(localStorage)
      .filter((key) =>
        key.startsWith(`${STORAGE_PREFIX}:`)
      )
      .forEach((key) =>
        localStorage.removeItem(key)
      );
  },
};