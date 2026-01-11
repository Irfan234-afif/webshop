import { createResource } from "frappe-ui"

const items = createResource({
    url: 'webshop.webshop.api.products.get_items_home',
    auto: false, // Don't auto-fetch, let Home.vue control when to fetch
    params: {},
    transform(data: any) {
        return data
    }
})

// Helper function to fetch items for a specific student
function fetchForStudent(studentName: string | null) {
    if (studentName) {
        items.update({
            params: { student: studentName }
        })
    } else {
        // Clear student parameter for guests
        items.update({
            params: {}
        })
    }
    items.fetch()
}

export { items, fetchForStudent };