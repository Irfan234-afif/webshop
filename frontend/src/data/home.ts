import { createResource } from "frappe-ui"

const items = createResource({
    url: 'webshop.webshop.api.products.get_items_home'
})

export { items };