/**
 * THE UNVEILING ATELIER — STATE MANAGER
 * Manages campaign inventory, active index, circular iteration, and metadata access.
 */
class AtelierState {
  constructor(campaignsData = []) {
    this.campaigns = campaignsData;
    this.currentIndex = 0;
    this.total = this.campaigns.length;
    this.isTransitioning = false;
    this.isAutoplayPaused = false;
  }

  getCurrent() {
    return this.campaigns[this.currentIndex] || null;
  }

  getNextIndex(offset = 1) {
    if (this.total === 0) return 0;
    return (this.currentIndex + offset + this.total) % this.total;
  }

  getNext(offset = 1) {
    const idx = this.getNextIndex(offset);
    return this.campaigns[idx] || null;
  }

  setCurrentIndex(index) {
    if (this.total === 0) return;
    this.currentIndex = ((index % this.total) + this.total) % this.total;
  }

  stepForward() {
    this.setCurrentIndex(this.currentIndex + 1);
    return this.getCurrent();
  }

  stepBackward() {
    this.setCurrentIndex(this.currentIndex - 1);
    return this.getCurrent();
  }
}

window.AtelierState = AtelierState;
