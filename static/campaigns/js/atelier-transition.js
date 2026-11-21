/**
 * THE UNVEILING ATELIER — CINEMATIC TRANSITION CONTROLLER
 * Coordinates architectural veil sweep, dual-buffered video crossfade,
 * staggered typography transitions, and odometer roll.
 */
class AtelierTransitionController {
  constructor(elements, state) {
    this.el = elements;
    this.state = state;
    this.activeVideoSlot = 1; // 1: videoPrimary, 2: videoSecondary
  }

  /**
   * Executes the signature Unveiling Transition to a target campaign
   * @param {Object} targetCampaign - The upcoming campaign data
   * @param {String} direction - 'forward' or 'backward'
   */
  async unveil(targetCampaign, direction = 'forward') {
    if (!targetCampaign) return;

    const currentCampaign = this.state.getCurrent();
    const nextUpcoming = this.state.getNext(1);

    // 1. Trigger architectural veil mask sweep
    if (this.el.veilMask) {
      this.el.veilMask.classList.remove('unveiling-forward', 'unveiling-backward');
      // Force reflow
      void this.el.veilMask.offsetWidth;
      this.el.veilMask.classList.add(direction === 'forward' ? 'unveiling-forward' : 'unveiling-backward');
    }

    // 2. Animate Zone A typography out (slide & fade)
    this.fadeTypographyOut();

    // 3. Prepare target video in inactive slot
    const incomingSlot = this.activeVideoSlot === 1 ? this.el.videoSecondary : this.el.videoPrimary;
    const outgoingSlot = this.activeVideoSlot === 1 ? this.el.videoPrimary : this.el.videoSecondary;

    // Detect if screen is mobile portrait
    const isMobile = window.innerWidth <= 640;
    const videoSrc = (isMobile && targetCampaign.video_mobile) ? targetCampaign.video_mobile : targetCampaign.video_desktop;
    const posterSrc = (isMobile && targetCampaign.poster_mobile) ? targetCampaign.poster_mobile : targetCampaign.poster_desktop;

    if (incomingSlot) {
      if (incomingSlot.getAttribute('data-src') !== videoSrc) {
        incomingSlot.src = videoSrc;
        incomingSlot.setAttribute('data-src', videoSrc);
        incomingSlot.load();
      }
    }

    // 4. Update poster fallback immediately under mask
    if (this.el.stagePoster) {
      this.el.stagePoster.src = posterSrc;
      this.el.stagePoster.classList.remove('hidden');
    }

    // 5. At veil midpoint (~480ms), swap contents, theme, and typography
    await this.wait(480);

    // Update Section Theme and Architectural Clip Style
    if (this.el.heroSection) {
      this.el.heroSection.setAttribute('data-active-theme', targetCampaign.theme_accent || 'gold');
    }
    if (this.el.stageViewport) {
      this.el.stageViewport.setAttribute('data-composition', targetCampaign.composition_style || 'sculptural-bevel');
    }

    // Update Odometer & Typography Texts
    this.updateOdometer(targetCampaign.order);
    this.updateTypographyContent(targetCampaign);

    // Fade Typography In with Stagger
    this.fadeTypographyIn();

    // Play incoming video & crossfade
    if (incomingSlot) {
      incomingSlot.currentTime = 0;
      const playPromise = incomingSlot.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            incomingSlot.classList.add('playing');
            if (this.el.stagePoster) this.el.stagePoster.classList.add('hidden');
          })
          .catch((err) => {
            console.warn('Autoplay prevented or video failed, showing poster:', err);
            if (this.el.stagePoster) this.el.stagePoster.classList.remove('hidden');
          });
      }
    }

    // Pause and hide outgoing video
    if (outgoingSlot) {
      outgoingSlot.classList.remove('playing');
      outgoingSlot.pause();
    }

    // Swap active slot pointer
    this.activeVideoSlot = this.activeVideoSlot === 1 ? 2 : 1;

    // Update Zone C upcoming collection preview
    this.updatePreviewCard(nextUpcoming);

    // Update slide indicator dots/pills
    this.updateSlidePills(this.state.currentIndex);

    // Wait for veil to complete exit
    await this.wait(600);
    if (this.el.veilMask) {
      this.el.veilMask.classList.remove('unveiling-forward', 'unveiling-backward');
    }
  }

  fadeTypographyOut() {
    const textEls = [
      this.el.storyEyebrow,
      this.el.storyHeadline,
      this.el.storyHeadlineSub,
      this.el.storyDescription,
      this.el.storyCuratorNote,
      this.el.storyProvenanceTag,
      this.el.storyCta
    ];
    textEls.forEach(el => {
      if (el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(12px)';
      }
    });
  }

  fadeTypographyIn() {
    const textEls = [
      { el: this.el.storyEyebrow, delay: 0 },
      { el: this.el.storyHeadline, delay: 60 },
      { el: this.el.storyHeadlineSub, delay: 120 },
      { el: this.el.storyDescription, delay: 180 },
      { el: this.el.storyCuratorNote, delay: 230 },
      { el: this.el.storyProvenanceTag, delay: 270 },
      { el: this.el.storyCta, delay: 310 }
    ];
    textEls.forEach(item => {
      if (item.el) {
        setTimeout(() => {
          item.el.style.opacity = '1';
          item.el.style.transform = 'translateY(0)';
        }, item.delay);
      }
    });
  }

  updateTypographyContent(data) {
    if (this.el.storyEyebrow) this.el.storyEyebrow.textContent = data.eyebrow;
    if (this.el.storyHeadline) this.el.storyHeadline.textContent = data.title;
    if (this.el.storyHeadlineSub) this.el.storyHeadlineSub.textContent = data.headline_sub || '';
    if (this.el.storyDescription) this.el.storyDescription.textContent = data.description;
    if (this.el.storyCuratorNote) this.el.storyCuratorNote.textContent = data.curator_note;
    if (this.el.storyProvenanceTag) this.el.storyProvenanceTag.textContent = data.provenance_tag;
    if (this.el.storyCtaText) this.el.storyCtaText.textContent = data.cta_text || 'EXPLORE COLLECTION';
    if (this.el.storyCta) this.el.storyCta.href = data.cta_url || '#';
  }

  updateOdometer(targetOrder) {
    if (this.el.catalogueOrder) this.el.catalogueOrder.textContent = targetOrder;
    if (!this.el.odometerDigit) return;
    this.el.odometerDigit.style.opacity = '0';
    this.el.odometerDigit.style.transform = 'translateY(-100%)';
    setTimeout(() => {
      this.el.odometerDigit.textContent = targetOrder;
      this.el.odometerDigit.style.transform = 'translateY(100%)';
      void this.el.odometerDigit.offsetWidth;
      this.el.odometerDigit.style.opacity = '1';
      this.el.odometerDigit.style.transform = 'translateY(0)';
    }, 250);
  }

  updatePreviewCard(upcomingCampaign) {
    if (!upcomingCampaign || !this.el.previewCard) return;
    if (this.el.previewOrder) this.el.previewOrder.textContent = `${upcomingCampaign.order} / ${String(this.state.total).padStart(2, '0')}`;
    if (this.el.previewEyebrow) this.el.previewEyebrow.textContent = upcomingCampaign.eyebrow;
    if (this.el.previewTitle) this.el.previewTitle.textContent = upcomingCampaign.title;
    if (this.el.previewImg) {
      this.el.previewImg.src = upcomingCampaign.poster_desktop;
      this.el.previewImg.alt = upcomingCampaign.title;
    }
  }

  updateSlidePills(activeIndex) {
    if (!this.el.slidePills) return;
    const pills = this.el.slidePills.querySelectorAll('.slide-pill-dot');
    pills.forEach((pill, idx) => {
      if (idx === activeIndex) {
        pill.classList.add('active');
        pill.setAttribute('aria-selected', 'true');
      } else {
        pill.classList.remove('active');
        pill.setAttribute('aria-selected', 'false');
      }
    });
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

window.AtelierTransitionController = AtelierTransitionController;
