document.addEventListener('DOMContentLoaded', () => {
    const timers = document.querySelectorAll('.timer');
    const completeLinks = document.querySelectorAll('.actions a[href*="complete"]');

  
    function createBurstAnimation(x, y) {
        new mojs.Burst({
            radius: { 0: 100 },
            angle: 45,
            count: 10,
            children: {
                shape: 'circle',
                radius: 10,
                fill: ['#FF5722', '#FFC107', '#8BC34A'],
                duration: 2000
            },
            x: x,
            y: y,
            opacity: { 1: 0 },
        }).play();
    }

 
    function updateTimers() {
        timers.forEach(timer => {
            const deadline = new Date(timer.getAttribute('data-deadline'));
            const now = new Date();
            const remainingTime = deadline - now;

            if (remainingTime <= 0) {
                timer.textContent = 'The deadline has passed';
                timer.classList.add('expired');
            } else {
                const days = Math.floor(remainingTime / (1000 * 60 * 60 * 24));
                const hours = Math.floor((remainingTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);

                timer.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            }
        });
    }

    
    function handleTaskComplete(event) {
        event.preventDefault();
        const link = event.currentTarget;
        const taskItem = link.closest('li');
        const { left, top } = taskItem.getBoundingClientRect();

        createBurstAnimation(left + window.scrollX + taskItem.offsetWidth / 2, top + window.scrollY + taskItem.offsetHeight / 2);
        
        setTimeout(() => {
            window.location.href = link.href;
        }, 1000);
    }

    completeLinks.forEach(link => {
        link.addEventListener('click', handleTaskComplete);
    });

    updateTimers();
    setInterval(updateTimers, 1000);
});